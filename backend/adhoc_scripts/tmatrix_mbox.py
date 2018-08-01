import pandas as pd
import numpy as np
import os
import requests
import sys

mapbox_url = 'https://api.mapbox.com/directions-matrix/v1/'
mapbox_apikey = os.getenv('MAPBOX_APIKEY')
# NOTE: output times are in _seconds_

def get_travel_times(lnglats, mode):
    print(len(lnglats))
    querystring = {"access_token":mapbox_apikey}
    url = mapbox_url+mode+'/'+';'.join([','.join([str(c) for c in coords]) for coords in lnglats])

    response = requests.request(
        "GET", url, 
        params=querystring
        )
    print(response.json(), gh_apikey,'\n')
    print(response.request.body)
    time_matrix = np.array(response.json()['durations'])
    return time_matrix

modes = {
    "hamo": "scooter",
    "car": "mapbox/driving",
    "bike": "bike",
    "walk": "foot"
}

if __name__=='__main__':
    # get mode of interest
    args = sys.argv
    mode =modes[args[1]]
    # load stations
    stations = pd.read_csv('stations.csv')
    lnglats = stations[['longitude','latitude']].values
    mask = np.ones(len(lnglats), dtype=np.bool)
    #mask[[range(15)]] = False
    # get time matrix
    time_matrix = pd.DataFrame(index = stations['id'], columns=stations['id'])
    time_matrix.iloc[mask,mask] = get_travel_times(lnglats[mask].tolist(), mode)
    # make it a dataframe and store
    time_matrix.to_csv('travel_times_matrix_'+args[1]+'.csv')