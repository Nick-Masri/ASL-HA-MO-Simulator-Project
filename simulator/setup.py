import simulator.variables.parameters as params
import simulator.variables.helpers as helpers

import numpy as np
import pandas as pd
from datetime import timedelta

##############################
# Variable Declarations ~ NM/MC
##############################


station_mapping = np.asscalar(np.load(params.station_data))
station_mapping_int = {int(k): v for k, v in station_mapping.items()}

state = pd.read_csv(params.parking_data)
helpers.fix_row_numbers(state, station_mapping_int)
# print(state[['station_id', 'parking_spots', 'idle_vehicles']])



employees_at_stations = params.employees_at_stations

mean_demand = np.load(params.mean_data)

demand_forecast_formatter = helpers.demand_forecast_formatter

time_length = mean_demand.shape[0]
station_length = mean_demand.shape[1]
demand_forecast_alt = demand_forecast_formatter(station_length, time_length, mean_demand)

raw_requests = np.load(params.customer_data)
cust_requests = helpers.format_instructions(raw_requests)



dt = 5  # minutes
timestepsize = timedelta(0, 60 * dt)  # in seconds
horizon = timedelta(0, 12 * 60 * dt)  # in seconds
thor = int(horizon.seconds / timestepsize.seconds)

stations = (pd.read_csv('./data/stations_state.csv').set_index('station_id'))

modes = ['walk','hamo','car','bike']

travel_times = {
    mode: helpers.parse_ttimes(mode, stations, timestepsize) for mode in modes
}

parking_per_station = {station: stations['parking_spots'].get(station) for station in stations.index.tolist()}
cars_per_station = {station: stations['idle_vehicles'].get(station) for station in stations.index.tolist()}

setup_vars = {'mapping': station_mapping_int, 'parking': parking_per_station,
              'employees': employees_at_stations, 'cars': cars_per_station, 'station_ids': stations}