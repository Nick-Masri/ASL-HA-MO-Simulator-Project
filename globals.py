import pandas as pd
import numpy as np


def import_travel_times(filename):
    return pd.read_csv(filename)


###############
# Travel Times
###############

# Initializing the travel time matrices. They're Pandas DataFrames. Use the get method to get times.
CAR_TRAVEL_TIMES = import_travel_times("./data/travel_times_matrix_car.csv")
PEDESTRIAN_TRAVEL_TIMES = import_travel_times("./data/travel_times_matrix_walk.csv")
BIKE_TRAVEL_TIMES = import_travel_times("./data/travel_times_matrix_bike.csv")
HAMO_TRAVEL_TIMES = import_travel_times("./data/travel_times_matrix_hamo.csv")



###############
# Stations
###############


STATION_MAPPING = np.asscalar(np.load('./data/10_days/station_mapping.npy'))
# in the form {logical index: Real Station Number}
STATION_MAPPING_INT = {int(v):int(k) for k,v in STATION_MAPPING.items()}

STATION_LIST = pd.to_numeric(CAR_TRAVEL_TIMES.columns.values[1:]).tolist()


###############
# People
###############

EMPLOYEE_LIST = []


# Customer Requests
# Imports them and puts them into a 3d array. Each list item in the outer list is a 5 min block
# Within the five minute blocks there are tuples that list every set of requests (origin, desitnation)

raw_requests = np.load('./data/10_days/hamo10days.npy')
np.set_printoptions(threshold=np.inf)


CUST_REQUESTS = []
count = 0
for req in raw_requests:
    request_indices = np.nonzero(req)
    # print(req[request_indices[0][0], request_indices[1][0]])
    # print(request_indices)
    temp = []
    num_of_requests = len(request_indices[0])  # Number of (o, d) NOT the number of requests per (o, d)
    if num_of_requests > 0:
        # print(request_indices)
        for request in range(num_of_requests):
            origin = request_indices[0][request]
            destination = request_indices[1][request]
            for num in range(int(req[origin][destination])):  # Loop for number of custs going from (o, d)
                temp.append((origin, destination))
                count += 1
    CUST_REQUESTS.append(temp)

# after_count = 0
# for t in CUST_REQUESTS:
#     after_count += len(t)
#
# print('Count {}'.format(count))
# print('after count {}'.format(after_count))

###############
# Instructions
###############

DRIVER_INSTRUCTIONS = []
PEDESTRIAN_INSTRUCTIONS = []