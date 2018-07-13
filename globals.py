import pandas as pd
import numpy as np



#######################
# Travel Times helper functions ~ MC
#######################

def import_travel_times(filename):
    return pd.read_csv(filename)

def format_travel_times(filename, station_mapping, station_mapping_int):
    graph = import_travel_times(filename)
    fix_row_numbers(graph, station_mapping_int)
    # Remove rows that aren't in the station_mapping
    graph = graph[graph['station_id'].isin(station_mapping_int.keys())]
    graph.set_index('station_id', inplace=True)
    fix_header(graph, station_mapping)
    columns = sorted(graph.columns)

    return graph[columns].values

def fix_header(graph, station_mapping):
    columns = graph.columns.to_series()
    temp = []
    col_to_drop = []
    for col in columns:
        try:
            temp.append(station_mapping[col])
        except:
            temp.append(col)
            col_to_drop.append(col)

    graph.columns = temp
    graph.drop(columns=col_to_drop, inplace=True)

def fix_row_numbers(graph, station_mapping):
    graph['station_id'] = graph['station_id'].replace(station_mapping)
    graph.sort_values(by=['station_id'], inplace=True)


###############
# Stations ~ MC
###############


STATION_MAPPING = np.asscalar(np.load('./data/10_days/station_mapping.npy'))
# in the form {Real Station Number: Logical Index}
STATION_MAPPING_INT = {int(k):v for k,v in STATION_MAPPING.items()}



###############
# Travel Times ~ MC
###############

# Initializing the travel time matrices. They're Numpy arrays. Use the get method  in classes.py to get times.

CAR_TRAVEL_TIMES = format_travel_times("./data/travel_times_matrix_car.csv", STATION_MAPPING, STATION_MAPPING_INT)
print(CAR_TRAVEL_TIMES)
PEDESTRIAN_TRAVEL_TIMES = format_travel_times("./data/travel_times_matrix_walk.csv", STATION_MAPPING, STATION_MAPPING_INT)
BIKE_TRAVEL_TIMES = format_travel_times("./data/travel_times_matrix_bike.csv", STATION_MAPPING, STATION_MAPPING_INT)
HAMO_TRAVEL_TIMES = format_travel_times("./data/travel_times_matrix_hamo.csv", STATION_MAPPING, STATION_MAPPING_INT)


###############
# People
###############

EMPLOYEE_LIST = []

###########################
# Customer Requests ~ MC
############################
# Imports them and puts them into a 3d array. Each list item in the outer list is a 5 min block
# Within the five minute blocks there are tuples that list every set of requests (origin, desitnation)
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



###############
# Instructions
###############

DRIVER_INSTRUCTIONS = []
PEDESTRIAN_INSTRUCTIONS = []

###############
# Forecast Demd Mean
###############

mean_demand = np.load('./data/mean_demand_weekday_5min.npy')
DEMAND_FORECAST = np.sum(mean_demand, axis=1)


