import pandas as pd
import numpy as np
import os
import requests
import datetime
import pytz
import grequests
import time

# NOTE: I NEED TO RECOMPUTE THE FUCKING TRAVEL TIMES. 
# NOTE: I NEED TO STILL PIPE EVERYTHING
# NOTE: CALLING STATION DETAIL IS A PAIN IN THE FUCKING ARSE


HAMO_URL = 'https://sp-ride.tp-tsc.com/omsp/external'
APIKEY = os.getenv('HAMO_APIKEY')
APIKEY = 'fe90c1fb84820b21c70edc4baab1c649'

#--- Initial Setup ---
# load travel times
modes = ['walk','hamo','car','bike']
def parse_ttimes(mode):
    tt = pd.read_csv(
            'travel_times_matrix_'+mode+'.csv', index_col=0
        ).dropna(axis=0, how='all').dropna(axis=1, how='all')
    tt.columns = [int(c) for c in tt.columns]
    return tt
travel_times = {
    mode: parse_ttimes(mode) for mode in modes
}
# get the stations
n_stations = len(travel_times['hamo'])
station_ids = travel_times['hamo'].index.tolist()
# road graph
roadGraph = [[list(range(n_stations))] for i in range(n_stations)]

road_network = {
    "roadGraph": roadGraph,
    "travelTimes": travel_times['hamo'].values,
    "driverTravelTimes": travel_times['bike'].values,
    "pvTravelTimes": travel_times['car'].values,
    "cTravelTimes": travel_times['car'].values
}

def get_available_stations():
    '''
    returns available stations
    '''
    # ping tmc
    querystring = {"zone_id":"1","lang":"en"}
    
    headers = {
        'omms_auth': APIKEY
        }
    url = HAMO_URL+"/station/list"
    response = requests.request("GET", url, headers=headers, params=querystring)
    stations = []
    for  area in response.json()['zone']['areas']:
        for station in  area['stations']:
            stations.append(station)    
    # return list of stations that are open 
    return stations

def get_station_state(station_ids):
    '''
    returns idle vehicles at each station in a dataframe
    '''
    idle_vehicles = np.zeros(len(station_ids))
    available_parking = np.zeros(len(station_ids))
    is_open = np.zeros(len(station_ids))
    headers = {
        'omms_auth': APIKEY
    }
    url = HAMO_URL+"/station/detail"
    reqs = []
    t1 = time.time()
    for i, s_id in enumerate(station_ids):
        #print "{}/{}, id: {}".format(i,len(station_ids),s_id)
        querystring = {"zone_id":"1","station_id":str(s_id),"lang":"en"}
        # response = requests.request("GET", url, headers=headers, params=querystring)
        reqs.append(grequests.get(url, headers=headers, params=querystring))
    print("sending requests")
    responses = grequests.map(reqs)
    for i,response in enumerate(responses):
        station = response.json()['station']
        idle_vehicles[i] = station['available_car']
        available_parking[i] = station['parking_space_free']
        is_open[i] = station['opening_flag_today']
    print("Time of requests: {}".format(time.time() - t1))
    stations_state = pd.DataFrame(index= station_ids)
    stations_state['idle_vehicles'] = idle_vehicles
    stations_state['available_parking'] = available_parking
    stations_state['is_open'] = is_open
    return stations_state

def get_total_parking_spots(stations_state, ongoing_trips):
    '''
    returns the total number of parking spots
    '''
    # aggregate ongoing_trips by dst
    ongoing_spots = ongoing_trips[['id','station_id_dst']].groupby('station_id_dst').count()
    spots = pd.DataFrame(index = stations_state.index)
    spots.loc[ongoing_spots.index,'ongoing'] = ongoing_spots['id'].values
    spots = spots.fillna(0)
    return stations_state['idle_vehicles'] + stations_state['available_parking'] + spots['ongoing']

def get_ongoing_trips(filter = True):
    # get them from the api
    querystring = {"zone_id":"1"}
    headers = {
        'omms_auth': APIKEY
    }
    url = HAMO_URL+"/carShare/list"
    response = requests.request("GET", url, headers=headers, params=querystring)
    ongoing_trips = pd.DataFrame(response.json()["carShare"])
    ongoing_trips['is_rebalancing_trip'] = ongoing_trips['status'].isin([91,92,93,94,95])
    # filter: if the trip has been ongoing for more than 24 hrs and it is a rebalancing trip
    ongoing_trips['registered_dt'] = pd.to_datetime(ongoing_trips['registered_dt']).dt.tz_localize('Asia/Tokyo')
    tz = pytz.timezone('Asia/Tokyo')
    current_japan_time = datetime.datetime(2018,0o3,29,8,0, tzinfo = tz)#.now(pytz.utc)
    #current_japan_time = current_japan_time.astimezone(pytz.timezone('Asia/Tokyo'))
    ongoing_trips['duration'] = current_japan_time - ongoing_trips['registered_dt']
    fishy_mask = (ongoing_trips['is_rebalancing_trip']) & (ongoing_trips['duration'].dt.days > 0)
    ongoing_trips = ongoing_trips[~fishy_mask]
    # filter: if the trip has not _started_ then we don't really care, we can't estimate ETA
    ongoing_trips = ongoing_trips.dropna(axis= 0, subset= ['start_dt'])
    # get ETA
    as_seconds = lambda t: datetime.timedelta(0,t)
    def get_time(series):
        tt = travel_times['hamo'].loc[series['station_id_org']][series['station_id_dst']]
        return as_seconds(tt)
    
    ongoing_trips['expected_duration'] = ongoing_trips.apply(
        get_time,
        axis = 1
        )
    ongoing_trips['start_dt'] = pd.to_datetime(ongoing_trips['start_dt']).dt.tz_localize('Asia/Tokyo')
    ongoing_trips['ETA'] = ongoing_trips['start_dt'] + ongoing_trips['expected_duration']
    # return them as such
    return ongoing_trips

if __name__ == '__main__':
    print(APIKEY)
    stations = get_available_stations()
    stations = pd.DataFrame(stations)
    stations = stations.set_index('station_id')
    # ACHTUNG: there are stations in okinawa and in Tokyo
    latmask = (35.0075 <= stations['station_lat']) & (stations['station_lat'] <= 35.16763)
    lngmask = (137.0585632 <= stations['station_lng']) & (stations['station_lng'] <= 137.2590637)
    mask = (latmask & lngmask).values
    stations = stations[mask]
    print(len(stations.index))
    stations_state = get_station_state(stations.index)
    print(len(stations_state.index))
    ongoing_trips = get_ongoing_trips()
    stations['parking_spots'] = get_total_parking_spots(stations_state, ongoing_trips)
    stations.to_csv('stations.csv', encoding = 'utf-8')
    for col in stations.columns:
        stations_state[col] = stations[col]
    stations_state.to_csv('tmp/stations_state.csv', encoding = 'utf-8')
    ongoing_trips.to_csv('tmp/ongoing.csv', index=False, encoding = 'utf-8')