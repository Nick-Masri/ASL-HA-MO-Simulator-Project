####################################
# Define Controller Type:
####################################

controller_type = 'smart'

####################################
# Variables for Initial State
####################################

station_mapping = np.asscalar(np.load('./data/10_days/station_mapping.npy'))
# in the form {Real Station Number: Logical Index}

cars_per_station = 5
# Dict of intial employee positions in the form {Station: number of employees

employees_at_stations = {22:1, 55:1}
text_file_output = []
station_dict = {}

total_time_full = np.zeros(shape=(58, 1))
total_time_empty = np.zeros(shape=(58, 1))

####################################
# Defining Locations of the Data
####################################
parking_data = "data/stations_state.csv"
parking_columns = [3,9]
mean_data = "./data/mean_demand_weekday_5min.npy"
car_data = "./data/travel_times_matrix_car.csv"
walking_data = "./data/travel_times_matrix_walk.csv"
hamo_data = "./data/travel_times_matrix_hamo.csv"

####################################
# Variables for Smart Controller:
####################################

####################################
# Variables for Naive Controller:
####################################


# Time
morningStart = 8
morningEnd = 10

eveningStart = 5
eveningEnd = 8








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

parking = {}
for item in locations:
    parking[station_mapping_int[item[0]]] = item[1]

station_dict = station_initializer(station_mapping_int, parking, employees_at_stations, cars_per_station)