import simulator.parameters
import simulator.helpers
import numpy as np
import pandas as pd

##############################
# Variable Declarations ~ NM/MC
##############################

station_mapping = np.asscalar(np.load(simulator.parameters.station_data))
station_mapping_int = {int(k): v for k, v in station_mapping.items()}

parking_csv = pd.read_csv(simulator.parameters.parking_data).iloc[:, simulator.parameters.parking_columns]
locations = parking_csv.values

parking = {}
for item in locations:
    parking[station_mapping_int[item[0]]] = item[1]

employees_at_stations = simulator.parameters.employees_at_stations
cars_per_station = simulator.parameters.cars_per_station

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