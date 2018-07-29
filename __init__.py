#!/usr/bin/python
from helpers import *
from init_helpers import *

from datetime import datetime, timedelta
import numpy as np

from controller.hamod import *

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
# CARS = [0 for i in range(58)]
# CARS[10] = 1
# Dict of intial employee positions in the form {Station: number of employees
employees_at_stations = {2: 2, 5: 2}
# employees_at_stations = {}
PARKING = {}

for i in range(58):
    PARKING[i] = 8
station_dict = station_initializer(STATION_MAPPING_INT, PARKING, employees_at_stations, CARS)

print("EMPLOYEE LIST")
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


RoadNetwork = {}
RoadNetwork['roadGraph'] = neighbor_list
RoadNetwork['travelTimes'] = hamo_travel_times
RoadNetwork['driverTravelTimes'] = walking_travel_times
RoadNetwork['pvTravelTimes'] = car_travel_times
RoadNetwork['cTravelTimes'] = car_travel_times
RoadNetwork['parking'] = np.array([10 for i in range(58)])


# print('ROADNETWORK')
# for k, v in RoadNetwork.items():
#     try:
#         print(k, v.shape)
#     except:
#         print(k, v)


######################################
# Creating Parameters Dictionary ~ NM
######################################

dt = 5  # minutes
time_step_size = timedelta(0, 60 * dt)  # in seconds
horizon = timedelta(0, 12 * 60 * dt)  # in seconds
time_horizon = int(horizon.seconds / time_step_size.seconds)
c_d = 10000.
c_r = (1. / time_horizon) * 0.0001 * 24. * c_d


Parameters = {}
Parameters['pvCap'] = 4.
# Parameters['pvCap'] = 0

# Parameters['pvLocation'] = 0
Parameters['driverRebalancingCost'] = c_r
Parameters['vehicleRebalancingCost'] = c_r
Parameters['pvRebalancingCost'] = c_r
Parameters['lostDemandCost'] = c_d
Parameters['thor'] = float(time_horizon)


# for k, v in Parameters.items():
#     print(k, type(v))


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
pedestrian_requests = [[] for i in range(len(station_dict))]

for time in range(60, len(cust_requests)):
    print("Time: {}".format(time))
    text_file_output.append("\nTime: {}".format(time))
    text_file_output.append('------------------------------------------------------')
    
    idle_vehicles = []
    idle_drivers = []

    vehicle_arrivals = np.zeros(shape=(len(station_dict), 12))
    driver_arrivals = np.zeros(shape=(len(station_dict), 12))

    customer_requests = cust_requests[time]

    errors = update(station_dict, customer_requests, time, driver_requests, pedestrian_requests)
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
            for i in range(time, time + 12):
                # if person.vehicle_id is not None:
                #     if person.destination_time == i:
                #         if isinstance(person, Employee):
                #             driver_arrivals[station][i - time] += 1
                #
                #         vehicle_arrivals[station][i - time] += 1
                #         break
                if person.destination_time == i:
                    print("Destinatiion time = i")
                    if isinstance(person, Employee):
                        driver_arrivals[station][i - time] += 1
                    if person.vehicle_id is not None:
                        vehicle_arrivals[station][i - time] += 1
                # else:
                #     break

        ########################################
        # Fraction of Time for at Capacity or Empty ~ JS
        ########################################

        num_parked_cars = len(station_dict[station].car_list)
        num_park_spots = 50 - len(station_dict[station].car_list)

        if num_parked_cars == 0:
            total_time_empty[station] += 1

        if num_parked_cars == num_park_spots:
            total_time_full[station] += 1

    print("Vehicle arrivals: {}".format(vehicle_arrivals.sum()))
    print("Driver arrivals: {}".format(driver_arrivals.sum()))
    ######################################
    # Creating Forecast Dictionary ~ NM/MC
    ######################################
    if controller_type == 'smart':
        Forecast = {
            # 'demand' : demand_forecast_parser(time), # ~ MC
            # 'demand' : np.ceil(demand_forecast_parser_alt(time)),
            'demand' : demand_forecast_parser_alt(time),
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
        try:
            controller
        except:
            controller = MoDController(RoadNetwork)

        # Other Fake State data for testing.
        # Parameters = np.load("./parameters.npy").item()
        # State = np.load("./state.npy").item()
        # Forecast = np.load("./forecast.npy").item()
        # Flags = np.load("./flags.npy").item()
        # np.save(os.path.join("./state/", str(time) + "roadNetwork.npy"), RoadNetwork)
        # np.save(os.path.join("./state/", str(time) + "parameters.npy"), Parameters)
        # np.save(os.path.join("./state/", str(time) + "state.npy"), State)
        # np.save(os.path.join("./state/", str(time) + "forecast.npy"), Forecast)
        [tasks, controller_output] = controller.computerebalancing(Parameters, State, Forecast, Flags)
        # for task in tasks:
        #     print(task)
        #
        # for c_output in controller_output:
        #     print(c_output)

    elif controller_type == 'naive':

        if morningStart  <= time and time <= morningEnd:
            morning_rebalancing(station_dict)
            morningStart += 24
            morningEnd += 24
        elif eveningStart <= time and time <= eveningEnd:
            evening_rebalancing(station_dict)
            eveningStart += 24
            eveningEnd += 24


    print('\n\n*****************************\n\n')
    print("Controller")

    for k,v in controller_output.items():
        if k != "cplex_out":
            print(k, v)

    text_file_output.append('Errors: {}'.format(errors))



    pedestrian_requests = tasks['driverRebalancingQueue']
    # for request in pedestrian_requests:
    #     print(request)
    vehicle_requests = tasks['vehicleRebalancingQueue']
    print(pedestrian_requests)
    print(vehicle_requests)

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