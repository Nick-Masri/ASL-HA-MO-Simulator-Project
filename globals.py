import pandas as pd
import numpy as np

import operator
import random
from itertools import repeat
random.seed(1477)


def import_travel_times(filename):
    return pd.read_csv(filename)

# Station Mapping
STATION_MAPPING = np.asscalar(np.load('./data/10_days/station_mapping.npy'))
STATION_MAPPING_INT = {int(v):int(k) for k,v in STATION_MAPPING.items()}
print(STATION_MAPPING_INT)
# print(STATION_MAPPING['4'])

# Initializing the travel time matrices. They're Pandas DataFrames. Use the get method to get times.
CAR_TRAVEL_TIMES = import_travel_times("./data/travel_times_matrix_car.csv")
PEDESTRIAN_TRAVEL_TIMES = import_travel_times("./data/travel_times_matrix_walk.csv")
BIKE_TRAVEL_TIMES = import_travel_times("./data/travel_times_matrix_bike.csv")
HAMO_TRAVEL_TIMES = import_travel_times("./data/travel_times_matrix_hamo.csv")

# Station List
STATION_LIST = pd.to_numeric(CAR_TRAVEL_TIMES.columns.values[1:]).tolist()



# Customer Requests
CUST_REQUESTS = np.load('./data/10_days/hamo10days.npy')
time1 = CUST_REQUESTS[0]
temp = np.nonzero(time1)
print(temp)
print(time1[17, 17])
for i in range(len(temp[0])):
    print(time1[temp[0][i], temp[1][i]])





####################
# INIT CONDITIONS #
##################


#################
# Instructions #
###############
