from flask import request, abort
from flask_restful import Resource, Api
from werkzeug.exceptions import HTTPException
import jwt
from jwt import DecodeError, ExpiredSignature
from datetime import datetime, timedelta
from functools import wraps
from flask import g
from database import User
import os
import requests
import grequests
import random
import pandas as pd
from controller import Controller
import pytz
import numpy as np
from scipy.stats import poisson
from .optimal_mod.modcontroller import test

#--- Initial Setup ---
RETURN_PAST_REB = False # if true it returns a prebaked historical rebalance
TEST_MORNING_RUSH = False
if TEST_MORNING_RUSH:
    STATION_STATE_PATH = 'adhoc_scripts/scenarios/s1/stations_state.csv'
else:
    STATION_STATE_PATH = 'adhoc_scripts/tmp/stations_state.csv'
dt = 5 # minutes
timestepsize = timedelta(0, 60*dt) # in seconds
horizon = timedelta(0, 12*60*dt) # in seconds
thor = int(horizon.seconds / timestepsize.seconds)
#timezone_name = 'America/Los_Angeles'
timezone_name = 'Asia/Tokyo'
# load stations
stations = pd.read_csv(STATION_STATE_PATH).set_index('station_id')
# load travel times
modes = ['walk','hamo','car','bike']
def parse_ttimes(mode):
    tt = pd.read_csv(
            'adhoc_scripts/travel_times_matrix_'+mode+'.csv', index_col=0
        ).dropna(axis=0, how='all').dropna(axis=1, how='all')
    tt.columns = [int(c) for c in tt.columns]
    tt.iloc[:,:] = np.ceil(tt.values.astype(np.float64) / float(timestepsize.seconds))
    # reorder to match the index
    tt = tt.loc[stations.index][stations.index]
    np.fill_diagonal(tt.values, 1)
    return tt
travel_times = {
    mode: parse_ttimes(mode) for mode in modes
}
assert len(travel_times['car'].index) == len(stations.index)
# get the stations
station_ids = stations.index.tolist()
n_stations = len(station_ids)
# road graph
# indices must be matlab friendly
roadGraph = [list(range(1,n_stations+1)) for i in range(n_stations)]

road_network = {
    "roadGraph": roadGraph,
    "travelTimes": travel_times['hamo'].values,
    "driverTravelTimes": travel_times['walk'].values,
    "pvTravelTimes": travel_times['car'].values,
    "cTravelTimes": travel_times['car'].values,
    "parking": stations['parking_spots'].values
}

#--- Setup ---
# NOTE: Pick the costs with care, the optimizer is using a mipgap tolerance
# and for large tolerances and large cost differences between lost demand
# and rebalancing costs, the movements of the rebalancers will easily fall
# within the tolerance, returning nonsense activities. 
# easy rule of thumb: T * C_R > Tol * Tot_Demand * C_D
c_d = 10000.
c_r = (1. / thor) * 0.0001 * 24. * c_d
control_parameters = {}
control_parameters['pvCap'] = 4.
control_parameters['driverRebalancingCost'] = c_r
control_parameters['vehicleRebalancingCost'] = c_r
control_parameters['pvRebalancingCost'] = c_r
control_parameters['lostDemandCost'] =  c_d
control_parameters['thor'] = float(int(horizon.seconds / timestepsize.seconds))

control_settings = {
    "RoadNetwork": road_network,
    "timestep_size": timestepsize,
    "station_ids": station_ids,
    "travel_times": travel_times,
    "horizon": horizon,
    "params": control_parameters,
    "stations": stations,
    "thor": int(horizon.seconds / timestepsize.seconds),
    "timezone_name": timezone_name
}

forecast_settings = {
    "day_forecast_path":'adhoc_scripts/mean_demand_weekday_5min.npy',
    "timestepsize":timestepsize,
    "horizon":2 * int(horizon.seconds / timestepsize.seconds), 
    "id_to_idx_path":"adhoc_scripts/station_mapping.npy"
}

# instantiate controller
controller = Controller(forecast_settings, control_settings)

def get_current_time():
    if TEST_MORNING_RUSH:
        return datetime(2018,3,29,7,0, tzinfo = pytz.timezone(timezone_name))
    return datetime.now(tz=pytz.timezone(timezone_name))

#--- General ---
class NotFound(HTTPException):
    code = 404
    data = {}

class DocumentsApi(Api):
    
    def init_app(self, app):
        super(DocumentsApi, self).init_app(app)
        app.after_request(self.add_cors_headers)

    def add_cors_headers(self, response):
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,User-Agent')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        response.headers.add('User-Agent', 'Flask')
        return response


#--- Auth ----
def create_token(user):
    payload = {
        'sub': user.id, # subject
        'iat': datetime.utcnow(), # issued at
        'exp': datetime.utcnow() + timedelta(days = 1)
    }
    print(os.getenv('SECRET_KEY'))
    token = jwt.encode(payload, os.getenv('SECRET_KEY'), algorithm = 'HS256')
    return token.decode('unicode_escape')

def parse_token(req):
    token = req.headers.get('Authorization').split()[1]
    return jwt.decode(token, os.getenv('SECRET_KEY'), algorithm = 'HS256')

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not request.headers.get('Authorization'):
            abort(401, 'Missing authorization header')

        try:
            payload = parse_token(request)
        except DecodeError:
            abort(401, 'Token is invalid')
        except ExpiredSignature:
            abort(401, 'Token has expired')

        g.user_id = payload['sub']

        return f(*args, **kwargs)

    return decorated_function

class Auth(Resource):

    def post(self):
        data = request.get_json(force=True)
        username = data['username']
        password = data['password']
        user = User.query.filter_by(username=username).first()
        if user == None:
            abort(401, 'invalid username/password')
        if user.check_password(password):
            token = create_token(user)
            return {'token': token}
        else:
            abort(401, 'invalid username/password')
        return response

class PrivateResource(Resource):
    method_decorators = [login_required]

#--- Stations ---
class Stations(PrivateResource):

    def get(self):
        # demand
        tz = pytz.timezone(timezone_name)
        # current_time = datetime(2018,3,29,7,0, tzinfo = tz)
        current_time = get_current_time()
        demand = controller.forecast_demand(current_time)
        # show the median of the customer distr
        stations['demand'] = poisson.ppf(0.5, demand.sum(axis=2).sum(axis=1))
        # cheating for now
        return stations.reset_index().rename({
            'station_id':'id', 
            'station_lat':'latitude', 
            'station_lng':'longitude'
            }, axis='columns').to_dict(orient = 'records')

        #--- MAYBE IN THE FUTURE ping toyota for current set of stations
        #url = os.getenv('HAMO_URL') + '/station/list'
        #querystring = {"zone_id":"1","lang":"en"}
        #headers = {
        #    'omms_auth': os.getenv('HAMO_APIKEY'),
        #    'Cache-Control': "no-cache",
        #}
        #response = requests.request("GET", url, headers=headers, params=querystring).json()
        #stations = []
        #for area in response["zone"]["areas"]:
        #    for station in area["stations"]:
        #        # hardcoding that they are within the toyota area
        #        valid_lat = 35.0075 <= station['station_lat'] <= 35.16763
        #        valid_lng = 137.0585632 <= station['station_lng'] <= 137.2590637
        #        if station["opening_flag_today"] and valid_lng and valid_lat:
        #            stations.append({
        #                    "id": station["station_id"],
        #                    "station_name": station["station_name"],
        #                    "area_name": area["area_name"],
        #                    "latitude": station["station_lat"],
        #                    "longitude": station["station_lng"],
        #                })
        #return stations

#--- Recompute ---
class RecomputeTasks(PrivateResource):
    def post(self):
        #TODO: # parse stations from request
        stations = request.get_json(force=True)
        print(stations)
        stations = pd.DataFrame(stations).rename({
            'id':'station_id',
            }, axis='columns').set_index('station_id').loc[station_ids]
        print(stations.head().index)
        mask = stations['rebalancers'] > 0
        print(stations.index[mask])
        #station_latlng = [[s['latitude'],s['longitude']] for s in stations]
        #TODO: # get travel times for walking, biking, driving, and
        #TODO: # call the forecaster for a near-term forecast
        current_time = get_current_time()
        controller.forecast_demand(current_time)
        #TODO: # call TMC API for current state of the system
        # just read the fucking ongoing trips
        stations_state = pd.read_csv(STATION_STATE_PATH).set_index('station_id').loc[station_ids]
        for col in stations.columns:
            stations_state[col] = stations[col]
        mask = stations_state['rebalancers'] > 0
        print(stations_state.index[mask])
        ongoing = pd.read_csv('adhoc_scripts/tmp/ongoing.csv')
        if RETURN_PAST_REB:
            return get_past_reb_tasks(stations_state)
        # and update the fucking crap
        controller.set_state(stations_state)
        controller.set_arrivals(ongoing, current_time)
        #TODO: # using forecast, current state, call MoD controller
        tasks = controller.compute_rebalancing()
        #TODO: # return the strategy to the frontend
        tasks = generate_friendly_tasks(
            tasks, 
            stations_state, 
            show_horizon = thor
            )
        return tasks


#--- Helper functions ---
gmaps_url = "https://maps.googleapis.com/maps/api/directions/json"
mode_settings = {
    "car": {
        "mode": "driving",
        "departure_time":"now",
        "key":os.getenv("GMAPS_APIKEY"),
    },
    "hamo": {
        "mode": "driving",
        "departure_time":"now",
        "key":os.getenv("GMAPS_APIKEY"),
        "avoid":"highways"
    },
    "walk": {
        "mode": "walking",
        "departure_time":"now",
        "key":os.getenv("GMAPS_APIKEY")
    },
    "bike": {
        "mode": "bicycling",
        "departure_time":"now",
        "key":os.getenv("GMAPS_APIKEY")
    },
}

def get_shortest_path(start_latlon, end_latlon, mode, fallback_mode = 'walk'):
    '''
    start_latlon: [float,float]
    end_latlon: [float,float]
    mode: str \in ['car','walk','bike']
    '''
    # build query
    querystring = mode_settings[mode]
    querystring['origin'] = ','.join(map(str,start_latlon))
    querystring['destination'] = ','.join(map(str,end_latlon))
    # call gmaps
    response = requests.request("GET", gmaps_url, params=querystring)
    directions = response.json()
    if len(directions["routes"]) == 0:
        # failed to find a rout, use fallback mode
        querystring = mode_settings[fallback_mode]
        querystring['origin'] = ','.join(map(str,start_latlon))
        querystring['destination'] = ','.join(map(str,end_latlon))
        response = requests.request("GET", gmaps_url, params=querystring)
        directions = response.json()
        mode = fallback_mode
    # get first route
    subtask = {
        "mode": mode,
        "encoded": True,
        "geometry": {
            "coordinates": directions["routes"][0]["overview_polyline"]["points"],
            "type": "LineString"
        }
    }
    return subtask

def build_gmaps_request(start_latlon, end_latlon, mode):
    querystring = mode_settings[mode]
    querystring['origin'] = ','.join(map(str,start_latlon))
    querystring['destination'] = ','.join(map(str,end_latlon))
    return grequests.get(gmaps_url, params=querystring)

def sync_gmaps_reqs(src_latlon, dst_latlon, mode):
    querystring = mode_settings[mode]
    querystring['origin'] = ','.join(map(str,src_latlon))
    querystring['destination'] = ','.join(map(str,dst_latlon))
    return requests.request("GET", gmaps_url, params=querystring)

def generate_friendly_tasks(tasks, stations, show_horizon = thor):
    '''
        tasks are a list of lists, wherein each list
        is of the following format
        [source, destination, departure_time, arrival_time, mode]
        all values are int

        TODO: match the routes to the actual times
        TODO: show the waiting times
    '''
    print(tasks)
    modes = {
        "vehicleRebalancing":"hamo",
        "driverRebalancing":"walk",
        "driverPassengerRebalancing":"car",
        "privateVehicleRebalancing":"car",
    }
    formatted_tasks = []
    for i, subtasks in enumerate(tasks):
        task = {
            "id": str(i),
            "name": "Task {}".format(i),
            "legs":[]
        }
        print("TASK {}".format(i), subtasks)
        reqs = []
        reqs_idx = []
        for j, (src_idx, dst_idx, tinit, tend, mode) in enumerate(subtasks):
            if tinit > show_horizon:
                continue
            mode = modes[mode]
            src_latlon = stations.iloc[src_idx][['station_lat','station_lng']].values.tolist()
            dst_latlon = stations.iloc[dst_idx][['station_lat','station_lng']].values.tolist()
            if False:#src_idx != dst_idx:
                reqs.append(sync_gmaps_reqs(src_latlon, dst_latlon, mode))
                reqs_idx.append(j)
            # set default values
            src_latlon.reverse()
            dst_latlon.reverse()
            # rounding function
            f = lambda x: round(x, 6)
            coords = [list(map(f, src_latlon)), list(map(f,dst_latlon))]
            encoded = False
            est_duration = round(((tend - tinit) * timestepsize).seconds / 60)
            if src_idx != dst_idx:
                description = "{} from {} to {} (est. {} minutes).".format(
                    mode.capitalize(),
                    stations.index[src_idx],
                    stations.index[dst_idx],
                    est_duration
                    )
            else:
                description = "Wait for {} minutes.".format(round(est_duration))
            subtask = {
                "description": description,
                "mode": mode,
                "encoded": encoded,
                "geometry": {
                    "coordinates": coords,
                    "type": "LineString"
                }
            }
            #print "Task {}: ".format(i), [src_idx, dst_idx, mode], subtask
            if False:#src_idx != dst_idx:
                print("Task {} Request:".format(i), reqs[-1].url)
            task["legs"].append(subtask)
        # call the responses
        responses = reqs#grequests.map(reqs)
        # try to give good routes
        for j in reqs_idx:
            subtask = task["legs"][j]
            src_idx = subtasks[j][0]
            dst_idx = subtasks[j][1]
            mode = modes[subtasks[j][-1]]
            try:
                directions = responses[j].json()
                subtask["geometry"]["coordinates"] = directions["routes"][0]["overview_polyline"]["points"]
                subtask["encoded"] = True
                #print "Task {}: ".format(i), [src_idx, dst_idx, mode], subtask
                #print directions["routes"]
            except:
                continue
        formatted_tasks.append(task)
    return formatted_tasks

#--- Dummy functions: REMOVE AFTER --- TODO HERE RAMON YOU WANTED TO CHOOSE ORIGIN

def get_past_reb_tasks(stations_state):
    past_reb = pd.read_csv('adhoc_scripts/scenarios/s1/hist_reb.csv')
    past_reb['start_dt'] = pd.to_datetime(past_reb['start_dt'])
    past_reb['end_dt'] = pd.to_datetime(past_reb['end_dt'])
    past_reb = past_reb.sort_values('start_dt')
    rebids = past_reb['omms_id'].unique().tolist()
    tasks = []
    for rebid in rebids:
        task = {
            "id": rebid,
            "name": "Task {}".format(rebid),
            "legs":[]
        }
        subtasks = past_reb[past_reb['omms_id'] == rebid]
        for s in range(len(subtasks)):
            past_subtask = subtasks.iloc[s]
            src = past_subtask['station_id_org']
            dst = past_subtask['station_id_dst']
            src_latlon = stations_state.loc[src][['station_lat','station_lng']].values.tolist()
            dst_latlon = stations_state.loc[dst][['station_lat','station_lng']].values.tolist()
            src_latlon.reverse()
            dst_latlon.reverse()
            f = lambda x: round(x, 6)
            coords = [list(map(f, src_latlon)), list(map(f,dst_latlon))]
            dt = (past_subtask['end_dt'] - past_subtask['start_dt']).seconds
            description = "Hamo from {} to {} (est. {} minutes)".format(
                    src,
                    dst,
                    round(dt / 60.)
                )
            subtask = {
                "description": description,
                "mode": 'hamo',
                "encoded": False,
                "geometry": {
                    "coordinates": coords,
                    "type": "LineString"
                }
            }
            task["legs"].append(subtask)
        tasks.append(task)
    return tasks


def generate_random_tasks(stations, ntasks = 5, nlegs = 3):
    random.shuffle(stations)
    tasks = []
    for t in range(ntasks) :
        # create task
        task = {
            "id":t,
            "name": "From ",
            "legs":[]
        }
        # choose origin
        origin = stations.pop()
        for l in range(min(nlegs,len(stations))):
            # choose destination
            destination = stations.pop()
            # choose mode
            mode = random.choice(list(mode_settings.keys()))
            task["name"] += origin["station_name"] + " " + \
                mode + destination["station_name"] + " " 
            # call Gmaps
            subtask = get_shortest_path(
                [origin['latitude'],origin['longitude']],
                [destination['latitude'],destination['longitude']],
                mode
                )
            # append to task
            task["legs"].append(subtask)
            # make dest origin
            origin = destination
        # append task to tasks
        tasks.append(task)
        return tasks

#--- Test API ---
class HelloWorld(Resource):
    def get(self):
        return {'hello':'world'}

class TestMoD(Resource):
    def get(self):
        print('running the mod test')
        test()
        return {'result':'It ran'}


#--- Setup API ---
api_path = '/api/v1'
api = DocumentsApi()
api.add_resource(HelloWorld, api_path+'/test')
api.add_resource(TestMoD, api_path+'/testmod')
api.add_resource(RecomputeTasks, api_path+'/recompute')
api.add_resource(Auth, api_path+'/login')
api.add_resource(Stations, api_path+'/stations')

