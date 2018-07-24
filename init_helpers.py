from setup_vars import *
import numpy as np
import pandas as pd


def format_travel_times(filename, station_mapping, station_mapping_int):
    graph = pd.read_csv(filename)
    fix_row_numbers(graph, station_mapping_int)

    # Remove rows that aren't in the station_mapping
    graph = graph[graph['station_id'].isin(station_mapping_int.values())]
    # Change the index to the station_id
    graph.set_index('station_id', inplace=True)
    # Use map to fix the headers
    fix_header(graph, station_mapping)
    # Get a sorted list of columns so we can return the matrix sorted
    columns = sorted(graph.columns)

    return np.ceil(graph[columns].values / 300).astype(int)

######################################
# Demand Forecast ~ MC
######################################


def demand_forecast_parser(time, demand_forecast, time_step):
    one_day = 1440 / time_step
    time = time % one_day
    first_11_time_blocks = demand_forecast[time:time + 11]

    time = time + 11
    next_12_time_blocks = np.sum(demand_forecast[time: time + 12], axis=0)
    parsed_demand = np.vstack((first_11_time_blocks, next_12_time_blocks))

    return parsed_demand


# def demand_forecast_parser_alt(time):
#     time = time % 288  # For dealing with multiple days
#     first_11_time_blocks = DEMAND_FORECAST_ALT[:, :, time:time + 11]
#     time += 11
#     next_12_time_blocks = np.sum(DEMAND_FORECAST_ALT[:, :, time: time + 12], axis=2)
#     parsed_demand = np.zeros((first_11_time_blocks.shape[0],
#                               first_11_time_blocks.shape[1],
#                               first_11_time_blocks.shape[2] + 1))
#
#     for station in range(first_11_time_blocks.shape[0]):
#         parsed_demand[station] = np.hstack((first_11_time_blocks[station], next_12_time_blocks[station].reshape((58, 1))))
#
#     return parsed_demand
#

########################
# Travel Times helper functions ~ MC
#######################


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



# Setting up Station Mapping ~ MC
station_mapping_int = {int(k): v for k, v in station_mapping.items()}

# Formatting Data ~ NM
car_travel_times = format_travel_times(car_data, station_mapping, station_mapping_int)
walking_travel_times = format_travel_times(walking_data, station_mapping, station_mapping_int)
hamo_travel_times = format_travel_times(hamo_data, station_mapping, station_mapping_int)
mean_demand = np.load(mean_data)

# Demand Forecaster ~ MC
time_length = mean_demand.shape[0]
station_length = mean_demand.shape[1]
demand_forecast_alt = demand_forecast_formatter(station_length, time_length, mean_demand)


# Setting up parking ~ NM
parking_csv = pd.read_csv(parking_data).iloc[:, parking_columns]
locations = parking_csv.values

parking  = {}
for item in locations:
    parking[station_mapping_int[item[0]]] = item[1]



station_dict = station_initializer(station_mapping_int, parking, employees_at_stations, cars_per_station)