import simulator.variables.parameters
import simulator.variables.helpers
import numpy as np
import pandas as pd

from datetime import timedelta

##############################
# Variable Declarations ~ NM/MC
##############################

station_mapping = np.asscalar(np.load(simulator.variables.parameters.station_data))
station_mapping_int = {int(k): v for k, v in station_mapping.items()}

state = pd.read_csv(simulator.variables.parameters.parking_data)
simulator.variables.helpers.fix_row_numbers(state, station_mapping_int)
# print(state[['station_id', 'parking_spots', 'idle_vehicles']])

parking = state['parking_spots'].values.astype(int)
cars_per_station = state['idle_vehicles'].values.astype(int)

employees_at_stations = simulator.variables.parameters.employees_at_stations

format_travel_times = simulator.variables.helpers.format_travel_times

car_data = simulator.variables.parameters.car_data
walking_data = simulator.variables.parameters.walking_data
hamo_data = simulator.variables.parameters.hamo_data
mean_data = simulator.variables.parameters.mean_data

car_travel_times = format_travel_times(car_data, station_mapping, station_mapping_int)
walking_travel_times = format_travel_times(walking_data, station_mapping, station_mapping_int)
hamo_travel_times = format_travel_times(hamo_data, station_mapping, station_mapping_int)
mean_demand = np.load(mean_data)

demand_forecast_formatter = simulator.variables.helpers.demand_forecast_formatter

time_length = mean_demand.shape[0]
station_length = mean_demand.shape[1]
demand_forecast_alt = demand_forecast_formatter(station_length, time_length, mean_demand)

raw_requests = np.load(simulator.variables.parameters.customer_data)
cust_requests = simulator.variables.helpers.format_instructions(raw_requests)

stations = pd.read_csv('./data/stations_state.csv').set_index('station_id')

dt = 5  # minutes
timestepsize = timedelta(0, 60 * dt)  # in seconds
horizon = timedelta(0, 12 * 60 * dt)  # in seconds
thor = int(horizon.seconds / timestepsize.seconds)

modes = ['walk','hamo','car','bike']

travel_times = {
    mode: simulator.variables.helpers.parse_ttimes(mode, stations, timestepsize) for mode in modes
}