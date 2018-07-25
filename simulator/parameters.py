####################################
# Variables for Initial State
####################################

# in the form {Real Station Number: Logical Index}

cars_per_station = 1
# Dict of intial employee positions in the form {Station: number of employees

employees_at_stations = {22:1, 55:1}
text_file_output = []
station_dict = {}


####################################
# Defining Locations of the Data
####################################
station_data = "./data/10_days/station_mapping.npy"
parking_data = "data/stations_state.csv"
parking_columns = [3,9]
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
morningStart = 8
morningEnd = 10

eveningStart = 5
eveningEnd = 8

