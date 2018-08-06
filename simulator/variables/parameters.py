####################################
# Variables for Initial State
####################################

employees_at_stations = {2: 2, 5: 2}
station_dict = {}

####################################
# Defining Locations of the Data
####################################
station_data = "./data/10_days/station_mapping.npy"
parking_data = "data/stations_state.csv"
mean_data = "./data/mean_demand_weekday_5min.npy"
car_data = "./data/travel_times_matrix_car.csv"
walking_data = "./data/travel_times_matrix_walk.csv"
hamo_data = "./data/travel_times_matrix_hamo.csv"
customer_data = "./data/10_days/hamo10days.npy"

####################################
# Variables for Smart Controller:
####################################

####################################
# Variables for Naive Controller:
####################################

# Time
morningStart = 72  # 6am
morningEnd = 96 # 8am


eveningStart = 180  # 3pm
eveningEnd = 204  # 5pm
