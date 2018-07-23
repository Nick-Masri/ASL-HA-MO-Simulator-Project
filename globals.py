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
    graph = graph[graph['station_id'].isin(station_mapping_int.values())]
    # Change the index to the station_id
    graph.set_index('station_id', inplace=True)
    # Use map to fix the headers
    fix_header(graph, station_mapping)
    # Get a sorted list of columns so we can return the matrix sorted
    columns = sorted(graph.columns)

    return np.ceil(graph[columns].values/300).astype(int)


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


def demand_forecast_formatter(station_length, time_length, mean_demand):
    """
    :param station_length: int Number of stations
    :param time_length: int Number of times we have data for
    :param mean_demand: T x N x N numpy array - the unformatted mean demand
    :return: the formatted numpy array. Now in the form N x N x T
    """
    demand_forecast_alt = np.zeros((station_length, station_length, time_length+24))

    for time in range(time_length):
        for origin in range(station_length):
            for destination in range(station_length):
                demand_forecast_alt[origin, destination, time] = mean_demand[time, origin, destination]

    # Add the first 24 days to the end to allow forecasting on times 265 - 288
    for station in range(len(demand_forecast_alt)):
        demand_forecast_alt[station] = np.hstack((demand_forecast_alt[station, :, :288], demand_forecast_alt[station, :, :24]))

    return demand_forecast_alt


###############
# Stations ~ MC
###############

STATION_MAPPING = np.asscalar(np.load('./data/10_days/station_mapping.npy'))
# in the form {Real Station Number: Logical Index}
STATION_MAPPING_INT = {int(k): v for k, v in STATION_MAPPING.items()}


###############
# People ~ NM
###############

EMPLOYEE_LIST = []

for i in range(len(STATION_MAPPING_INT)):
    EMPLOYEE_LIST.append([])


# EMPLOYEE_LIST[0] = temp  # What is this?


###############
# Forecast Demand Mean ~ MC
###############

mean_demand = np.load('./data/mean_demand_weekday_5min.npy')

# This is in the format TxNxN which is not the right format for the controller
# DEMAND_FORECAST = np.sum(mean_demand, axis=1)

time_length = mean_demand.shape[0]
station_length = mean_demand.shape[1]

DEMAND_FORECAST_ALT = demand_forecast_formatter(station_length, time_length, mean_demand)








