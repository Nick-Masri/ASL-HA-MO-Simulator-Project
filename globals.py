import pandas as pd
import numpy as np


def import_travel_times(filename):
    return pd.read_csv(filename)


# Station Mapping
STATION_MAPPING = np.asscalar(np.load('./data/10_days/station_mapping.npy'))
# in the form {logical index: Real Station Number}
STATION_MAPPING_INT = {int(v):int(k) for k,v in STATION_MAPPING.items()}



# Initializing the travel time matrices. They're Pandas DataFrames. Use the get method to get times.
CAR_TRAVEL_TIMES = import_travel_times("./data/travel_times_matrix_car.csv")
PEDESTRIAN_TRAVEL_TIMES = import_travel_times("./data/travel_times_matrix_walk.csv")
BIKE_TRAVEL_TIMES = import_travel_times("./data/travel_times_matrix_bike.csv")
HAMO_TRAVEL_TIMES = import_travel_times("./data/travel_times_matrix_hamo.csv")

# Station List
STATION_LIST = pd.to_numeric(CAR_TRAVEL_TIMES.columns.values[1:]).tolist()


CAR_LIST = []

# (id from 0 to 5*len(STATION_Mapping), (station in Station_mapping))
#
# for station in STATION_MAPPING_INT:
#
#
#     CAR_LIST.append((id ), )

# Customer Requests
# Imports them and puts them into a 3d array. Each list item in the outer list is a 5 min block
# Within the five minute blocks there are tuples that list every set of requests (origin, desitnation)

raw_requests = np.load('./data/10_days/hamo10days.npy')


CUST_REQUESTS = []
for req in raw_requests:
    request_block = np.nonzero(req)
    temp = []
    if len(request_block[0]) > 0:
        for num in range(len(request_block)-1):
            temp.append((request_block[0][num], request_block[1][num]))
    CUST_REQUESTS.append(temp)


