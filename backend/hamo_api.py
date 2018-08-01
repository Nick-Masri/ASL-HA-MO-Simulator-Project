import requests
import pandas as pd
import numpy as np
from collections import OrderedDict
import pytz
import datetime
import os

HAMO_URL = os.getenv('HAMO_URL')
APIKEY = os.getenv('HAMO_APIKEY')

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
    stations = [station for station in area['stations'] for area in response.json()['zone']['areas']]
    # return list of stations that are open 
    return stations

def get_travel_times():
    pass

def get_trip_times():
    '''
    TODO: This needs to fetch the expected customer travel times
    '''
    return travel_times['car']

def get_station_state(station_ids):
    '''
    returns idle vehicles at each station in a dataframe
    '''
    idle_vehicles = np.array(len(station_ids))
    available_parking = np.array(len(station_ids))
    is_open = np.array(len(station_ids))
    headers = {
        'omms_auth': APIKEY
    }
    url = HAMO_URL+"/station/detail"
    for i, s_id in enumerate(station_ids):
        querystring = {"zone_id":"1","station_id":str(s_id),"lang":"en"}
        response = requests.request("GET", url, headers=headers, params=querystring)
        station = response.json()['station']
        idle_vehicles[i] = station['available_car']
        available_parking[i] = station['parking_space_free']
        is_open[i] = station['opening_flag_today']
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
    ongoing_spots = ongoing_trips[['id','station_id_dst']].group_by('station_id_dst').count()
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
    ongoing_trips = pd.DataFrame(response["carShare"])
    ongoing_trips['is_rebalancing_trip'] = ongoing_trips['status'].isin([91,92,93,94,95])
    # filter: if the trip has been ongoing for more than 24 hrs and it is a rebalancing trip
    current_japan_time = datetime.datetime.now(pytz.utc)
    current_japan_time = current_japan_time.astimezone(pytz.timezone('Asia/Tokyo'))
    ongoing_trips['duration'] = current_japan_time - ongoing_trips['registered_dt']
    fishy_mask = (ongoing_trips['is_rebalancing_trip']) & (ongoing_trips['duration'].dt.days > 0)
    ongoing_trips = ongoing_trips[fishy_mask]
    # filter: if the trip has not _started_ then we don't really care, we can't estimate ETA
    ongoing_trips = ongoing_trips.dropna(axis= 0, subset= ['start_dt'])
    # get ETA
    as_seconds = lambda t: datetime.timedelta(0,t)
    ongoing_trips['expected_duration'] = ongoing_trips.apply(
        lambda series: as_seconds(travel_times['hamo'][series['station_id_org']][series['station_id_dst']]),
        axis = 1
        )
    ongoing_trips['ETA'] = ongoing_trips['start_dt'] + ongoing_trips['expected_duration']
    # return them as such
    return ongoing_trips

def get_past_customer_demand():
    pass

