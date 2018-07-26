#!/usr/bin/python
from helpers import *
from init_helpers import *

from datetime import datetime, timedelta
import time
import numpy as np

from controller.hamod import *
from backend.controller import Controller

# Setup Variables
text_file_output = []
station_dict = {}

total_time_full = np.zeros(shape=(58, 1))
total_time_empty = np.zeros(shape=(58, 1))

controller_type = 'smart'
morningStart = 8
morningEnd = 10


eveningStart = 5
eveningEnd = 8

######################################
# Initializing Stations ~ MC/NM
######################################

# Dict of intial employee positions in the form {Station: number of employees
employees_at_stations = {2: 2, 5: 2}

# CARS = [0 for i in range(58)]
# CARS[10] = 1
station_dict = station_initializer(STATION_MAPPING_INT, PARKING, employees_at_stations, CARS)



print("Parking")
print("**************")
for station in station_dict:
    print("Station: {}, Parking: {}, Cars: {}"
          .format(station, station_dict[station].parking_spots, len(station_dict[station].car_list)))
######################################
# Creating Road Network Dictionary ~ NM/MC
######################################

neighbor_list = []
num_of_stations = len(STATION_MAPPING_INT)

# Indexed 1 (assumes logical indices)
for station in range(1, num_of_stations + 1):
    # Excluding the current station from the list of neighbors
    # lst = [i for i in range(1, num_of_stations + 1) if i != station]
    # neighbor_list.append(np.asarray(lst).reshape((1, num_of_stations - 1)))

    # Stations that share an edge with all other stations
    lst = [i for i in range(1, num_of_stations + 1)]
    neighbor_list.append(np.asarray(lst).reshape((1, num_of_stations)))


car_travel_times = format_travel_times("./data/travel_times_matrix_car.csv", STATION_MAPPING, STATION_MAPPING_INT)
walking_travel_times = format_travel_times("./data/travel_times_matrix_walk.csv", STATION_MAPPING, STATION_MAPPING_INT)
hamo_travel_times = format_travel_times("./data/travel_times_matrix_hamo.csv", STATION_MAPPING, STATION_MAPPING_INT)

dt = 5 # minutes
timestepsize = timedelta(0, 60*dt) # in seconds
horizon = timedelta(0, 12*60*dt) # in seconds
thor = int(horizon.seconds / timestepsize.seconds)

# Get info about stations from the station csv
stations = pd.read_csv('./data/stations_state.csv').set_index('station_id')
station_ids = stations.index.tolist()
n_stations = len(station_ids)

c_d = 10000.
c_r = (1. / thor) * 0.0001 * 24. * c_d
control_parameters = {}
control_parameters['pvCap'] = 4.
control_parameters['driverRebalancingCost'] = c_r
control_parameters['vehicleRebalancingCost'] = c_r
control_parameters['pvRebalancingCost'] = c_r
control_parameters['lostDemandCost'] =  c_d
control_parameters['thor'] = float(int(horizon.seconds / timestepsize.seconds))


modes = ['walk','hamo','car','bike']
def parse_ttimes(mode):
    tt = pd.read_csv(
            'data/travel_times_matrix_'+mode+'.csv', index_col=0
        ).dropna(axis=0, how='all').dropna(axis=1, how='all')
    tt.columns = [int(c) for c in tt.columns]
    tt.iloc[:,:] = np.ceil(tt.values.astype(np.float64) / float(timestepsize.seconds))
    # reorder to match the index
    tt = tt.loc[stations.index][stations.index]
    np.fill_diagonal(tt.values, 1)
    return tt
travel_times = {
    mode: parse_ttimes(mode) for mode in modes
}

print("****************")
print("****************")
print("****************")
print(travel_times['walk'])

road_network = {
    "roadGraph": neighbor_list,
    "travelTimes": travel_times['hamo'].values,
    "driverTravelTimes": travel_times['walk'].values,
    "pvTravelTimes": travel_times['car'].values,
    "cTravelTimes": travel_times['car'].values,
    "parking": stations['parking_spots'].values
}

######################################
# Creating Parameters Dictionary ~ NM
######################################




control_settings = {
    "RoadNetwork": road_network,
    "timestep_size": timestepsize,
    "station_ids": station_ids,
    "travel_times": travel_times,
    "horizon": horizon,
    "params": control_parameters,
    "stations": stations,
    "thor": int(horizon.seconds / timestepsize.seconds),
    "timezone_name": 'Asia/Tokoyo'
}

forecast_settings = {
    "day_forecast_path":'data/mean_demand_weekday_5min.npy',
    "timestepsize":timestepsize,
    "horizon":2 * int(horizon.seconds / timestepsize.seconds),
    "id_to_idx_path":"data/10_days/station_mapping.npy"
}


# for k, v in Parameters.items():
#     print(k, type(v))

controller = Controller(forecast_settings, control_settings)

######################################
# Creating Flags Dictionary ~ JS
######################################

# FLAGS = {'debugFlag': True is debugging, False if not, 'glpkFlag': True is using glpk, False is using cplex}
Flags = {'debugFlag': False, 'glpkFlag': False}

######################################
# Main Loop ~ NM
######################################


raw_requests = np.load('./data/10_days/hamo10days.npy')
cust_requests = format_instructions(raw_requests)
driver_requests = [[] for i in range(len(station_dict))]
driver_requests = [[] for i in range(len(station_dict))]
pedestrian_requests = [[] for i in range(len(station_dict))]

for curr_time in range(60, len(cust_requests)):
    print("Time: {}".format(curr_time))
    text_file_output.append("\nTime: {}".format(curr_time))
    text_file_output.append('------------------------------------------------------')
    
    idle_vehicles = []
    idle_drivers = []

    vehicle_arrivals = np.zeros(shape=(len(station_dict), 12))
    driver_arrivals = np.zeros(shape=(len(station_dict), 12))

    customer_requests = cust_requests[curr_time]

    errors = update(station_dict, customer_requests, curr_time, driver_requests, pedestrian_requests)
    # for station in station_dict:
    #     print('******************')
    #     print(station_dict[station].car_list)
    #     print('*******************')
    # Logging current state
    for station in sorted(station_dict):

        ######################################
        # Writing to text_file_output Files ~ NM
        ######################################

        text_file_output.append('\tStation: {}'.format(station))
        text_file_output.append('\t\tNumber of Idle Vehicles: {}'.format(len(station_dict[station].car_list)))
        text_file_output.append('\t\tAvailable Parking: {}'.format(50 - len(station_dict[station].car_list)))
        text_file_output.append('\t\tNum People En_Route: {}'.format(len(station_dict[station].get_en_route_list())))

        ############################################
        # Setting Up Idle Vehicles and Drivers ~ JS
        ############################################

        idle_vehicles.append(len(station_dict[station].car_list))
        idle_drivers.append(len(station_dict[station].employee_list))

        ########################################
        # Updating Vehicle/Driver Arrivals ~ NM
        ########################################

        for person in station_dict[station].get_en_route_list(True):
            for i in range(curr_time, curr_time + 12):
                # if person.vehicle_id is not None:
                #     if person.destination_time == i:
                #         if isinstance(person, Employee):
                #             driver_arrivals[station][i - time] += 1
                #
                #         vehicle_arrivals[station][i - time] += 1
                #         break
                if person.destination_time == i:
                    if isinstance(person, Employee):
                        driver_arrivals[station][i - curr_time] += 1
                    if person.vehicle_id is not None:
                        vehicle_arrivals[station][i - curr_time] += 1
                else:
                    break

        ########################################
        # Fraction of Time for at Capacity or Empty ~ JS
        ########################################

        num_parked_cars = len(station_dict[station].car_list)
        num_park_spots = 50 - len(station_dict[station].car_list)

        if num_parked_cars == 0:
            total_time_empty[station] += 1

        if num_parked_cars == num_park_spots:
            total_time_full[station] += 1

    ######################################
    # Creating Forecast Dictionary ~ NM/MC
    ######################################
    if controller_type == 'smart':
        Forecast = {
            # 'demand' : demand_forecast_parser(time), # ~ MC
            'demand' : np.ceil(demand_forecast_parser_alt(curr_time)),
            # 'demand' : demand_forecast_parser_alt(time),
            'vehicleArrivals': vehicle_arrivals, # ~ NM
            'driverArrivals' : driver_arrivals, # ~ NM
        }

        # print("FORECAST")
        # for k, v in Forecast.items():
        #     print(k, v.shape)

        ######################################
        # Creating State Dictionary ~ JS
        ######################################

        State = {
            'idleVehicles': np.array(idle_vehicles),
            'idleDrivers': np.array(idle_drivers),
            'privateVehicles': np.zeros((58,1)),
            'pvLocation': 0
        }

        # Fake data RoadNetwork
        # RoadNetwork = np.load("./roadNetwork.npy").item()

        # create controller if it doesn't already exist
        # try:
        #     controller
        # except:
        #     controller = MoDController(RoadNetwork)


        controller.forecast_demand(curr_time)
        controller.update_state_arrivals(Forecast, State)

        [tasks, paths] = controller.compute_rebalancing()


        print("******************")
        print("******************")
        print("******************")
        for k, v in tasks.items():
            print(k, v)

        for path in paths:
            print(path)


    elif controller_type == 'naive':

        if morningStart  <= curr_time and curr_time <= morningEnd:
            morning_rebalancing(station_dict)
            morningStart += 24
            morningEnd += 24
        elif eveningStart <= curr_time and curr_time <= eveningEnd:
            evening_rebalancing(station_dict)
            eveningStart += 24
            eveningEnd += 24




    text_file_output.append('Errors: {}'.format(errors))



    pedestrian_requests = tasks['driverRebalancingQueue']

    vehicle_requests = tasks['vehicleRebalancingQueue']
    text_file_output.append('Errors: {}'.format(errors))

    # driver_requests = format_instructions(text_file_output_requests)
    # customer_requests = format_instructions(text_file_output_requests)


######################################
# Tracking Errors / Summing Errors ~ JS
######################################

sum_station_no_park_errors = np.sum(no_park_errors, axis=0)  # no parking errors per station total
sum_station_no_car_cust_errors = np.sum(no_car_cust_errors, axis=0)  # no car available for customers errors per station
sum_station_no_car_emp_errors = np.sum(no_car_emp_errors, axis=0)  # no car available for employees errors per station

sum_time_no_park_errors = np.sum(no_park_errors, axis=1)  # no parking errors per time total
sum_time_no_car_cust_errors = np.sum(no_car_cust_errors, axis=1)  # no car available for customers errors per time total
sum_time_no_car_emp_errors = np.sum(no_car_emp_errors, axis=1)  # no car available for employees errors per time total


######################################
# Writing to text_file_output File ~ NM
######################################

text_file_output_file = open('text_file_output.txt', 'w')

for item in text_file_output:
    text_file_output_file.write("%s\n" % item)

text_file_output_file.close()