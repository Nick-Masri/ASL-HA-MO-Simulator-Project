import pandas as pd
import numpy as np
import os
import requests
import sys

graphhopper_url = 'https://graphhopper.com/api/1/matrix'
gh_apikey = os.getenv('GHOPPER_APIKEY')
# NOTE: output times are in _seconds_

def get_travel_times(lnglats, mode):
    print(len(lnglats))
    querystring = {"key":gh_apikey}
    payload = {
        "elevation":False,
        "out_arrays":["times"],
        "points":lnglats,
        "vehicle": mode 
    }
    headers = {
        'Content-Type': "application/json",
    }
    response = requests.request(
        "POST", graphhopper_url, 
        json=payload, headers=headers, params=querystring
        )
    #print response.json(), gh_apikey,'\n'
    #print response.request.body
    time_matrix = np.array(response.json()['times'])
    return time_matrix

modes = {
    "hamo": "scooter",
    "car": "car",
    "bike": "bike",
    "walk": "foot"
}

if __name__=='__main__':
    # get mode of interest
    args = sys.argv
    mode =modes[args[1]]
    # load stations
    stations = pd.read_csv('stations_state.csv')
    lnglats = stations[['station_lng','station_lat']].values
    # ACHTUNG: there are stations in okinawa and in Tokyo
    latmask = (35.0075 <= stations['station_lat']) & (stations['station_lat'] <= 35.16763)
    lngmask = (137.0585632 <= stations['station_lng']) & (stations['station_lng'] <= 137.2590637)
    mask = (latmask & lngmask).values
    # get time matrix
    time_matrix = pd.DataFrame(index = stations['station_id'], columns=stations['station_id'])
    time_matrix.iloc[mask,mask] = get_travel_times(lnglats[mask].tolist(), mode)
    # make it a dataframe and store
    time_matrix.to_csv('travel_times_matrix_'+args[1]+'.csv')