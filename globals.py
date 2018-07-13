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
# People ~ NM
###############
EMPLOYEE_LIST = []


for i in range(len(STATION_MAPPING_INT)):
    EMPLOYEE_LIST.append([])

EMPLOYEE_LIST[0] = [4]
###############
# Forecast Demand Mean ~ MC
###############

mean_demand = np.load('./data/mean_demand_weekday_5min.npy')
DEMAND_FORECAST = np.sum(mean_demand, axis=1)


