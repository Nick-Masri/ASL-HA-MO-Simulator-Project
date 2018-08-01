import pandas as pd
import numpy as np
import os
import requests


# NOTE: I NEED TO RECOMPUTE THE FUCKING TRAVEL TIMES. 
# NOTE: I NEED TO STILL PIPE EVERYTHING
# NOTE: CALLING STATION DETAIL IS A PAIN IN THE FUCKING ARSE


HAMO_URL = 'https://sp-ride.tp-tsc.com/omsp/external'
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
    stations = []
    for  area in response.json()['zone']['areas']:
    	for station in  area['stations']:
    		stations.append(station)    
    # return list of stations that are open 
    return stations

if __name__ == '__main__':
	stations = get_available_stations()
	stations = pd.DataFrame(stations)
	stations.to_csv('stations.csv', index = False, encoding = 'utf-8')