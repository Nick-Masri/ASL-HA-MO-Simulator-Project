import pandas as pd
import numpy as np

import random
from itertools import repeat
random.seed(1477)


def import_travel_times(filename):
    return pd.read_csv(filename)


cust_requests = np.load('./data/10_days/hamo10days.npy')
print(cust_requests.shape)


# hp.print_a_thing("This is a thing")

# Initializing the travel time matrices. They're Pandas DataFrames. Use the get method to get times.
CAR_TRAVEL_TIMES = import_travel_times("./data/travel_times_matrix_car.csv")
PEDESTRIAN_TRAVEL_TIMES = import_travel_times("./data/travel_times_matrix_walk.csv")
BIKE_TRAVEL_TIMES = import_travel_times("./data/travel_times_matrix_bike.csv")
HAMO_TRAVEL_TIMES = import_travel_times("./data/travel_times_matrix_hamo.csv")

# Station List
STATION_LIST = pd.to_numeric(CAR_TRAVEL_TIMES.columns.values[1:]).tolist()

# Station Mapping
STATION_MAPPING = np.load('.data/10_days/station_mapping.npy')

# Customer Requests
CUST_REQUESTS = np.load('.data/10_days/hamo10days.npy')



####################
# INIT CONDITIONS #
##################


#################
# Instructions #
###############
