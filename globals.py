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
# in the form {logical index: Real Station Number}
STATION_MAPPING_INT = {int(k):v for k,v in STATION_MAPPING.items()}


###############
# Travel Times ~ MC
###############

# Initializing the travel time matrices. They're Numpy arrays. Use the get method  in classes.py to get times.

CAR_TRAVEL_TIMES = format_travel_times("./data/travel_times_matrix_car.csv", STATION_MAPPING, STATION_MAPPING_INT)
PEDESTRIAN_TRAVEL_TIMES = format_travel_times("./data/travel_times_matrix_walk.csv", STATION_MAPPING, STATION_MAPPING_INT)
BIKE_TRAVEL_TIMES = format_travel_times("./data/travel_times_matrix_bike.csv", STATION_MAPPING, STATION_MAPPING_INT)
HAMO_TRAVEL_TIMES = format_travel_times("./data/travel_times_matrix_hamo.csv", STATION_MAPPING, STATION_MAPPING_INT)


###############
# People ~ NM
###############
EMPLOYEE_LIST = []


for i in range(len(STATION_MAPPING_INT)):
    EMPLOYEE_LIST.append([])

EMPLOYEE_LIST[0] = [1,2,3,4]
print(EMPLOYEE_LIST)
###############
# Forecast Demand Mean ~ MC
###############

mean_demand = np.load('./data/mean_demand_weekday_5min.npy')
DEMAND_FORECAST = np.sum(mean_demand, axis=1)


