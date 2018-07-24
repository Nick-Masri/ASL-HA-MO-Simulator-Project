import numpy as np
import pandas as pd

# Define Controller Type:
controller_type = 'smart'

station_mapping = np.asscalar(np.load('./data/10_days/station_mapping.npy'))
# in the form {Real Station Number: Logical Index}

cars_per_station = 5
# Dict of intial employee positions in the form {Station: number of employees
employees_at_stations = {2: 2, 5: 2}


employee_list = []

for i in range(len(station_mapping)):
    employee_list.append([])


text_file_output = []
station_dict = {}

total_time_full = np.zeros(shape=(58, 1))
total_time_empty = np.zeros(shape=(58, 1))


parking_data = "data/stations_state.csv"
parking_columns = [3,9]
mean_data = "./data/mean_demand_weekday_5min.npy"
car_data = "./data/travel_times_matrix_car.csv"
walking_data = "./data/travel_times_matrix_walk.csv"
hamo_data = "./data/travel_times_matrix_hamo.csv"

# Variables for Smart Controller:

# Variables for Naive Controller:


morningStart = 8
morningEnd = 10


eveningStart = 5
eveningEnd = 8

