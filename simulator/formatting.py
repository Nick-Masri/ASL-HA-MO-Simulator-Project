import simulator.parameters
import simulator.helpers
import numpy as np
import pandas as pd

##############################
# Variable Declarations ~ NM/MC
##############################

station_mapping = np.asscalar(np.load(simulator.parameters.station_data))
station_mapping_int = {int(k): v for k, v in station_mapping.items()}

state = pd.read_csv(simulator.parameters.parking_data)
simulator.helpers.fix_row_numbers(state, station_mapping_int)
# print(state[['station_id', 'parking_spots', 'idle_vehicles']])

parking = state['parking_spots'].values
cars_per_station = state['idle_vehicles'].values

employees_at_stations = simulator.parameters.employees_at_stations

format_travel_times = simulator.helpers.format_travel_times

car_data = simulator.parameters.car_data
walking_data = simulator.parameters.walking_data
hamo_data = simulator.parameters.hamo_data
mean_data = simulator.parameters.mean_data

car_travel_times = format_travel_times(car_data, station_mapping, station_mapping_int)
walking_travel_times = format_travel_times(walking_data, station_mapping, station_mapping_int)
hamo_travel_times = format_travel_times(hamo_data, station_mapping, station_mapping_int)
mean_demand = np.load(mean_data)

demand_forecast_formatter = simulator.helpers.demand_forecast_formatter

time_length = mean_demand.shape[0]
station_length = mean_demand.shape[1]
demand_forecast_alt = demand_forecast_formatter(station_length, time_length, mean_demand)

raw_requests = np.load(simulator.parameters.customer_data)
cust_requests = simulator.helpers.format_instructions(raw_requests)