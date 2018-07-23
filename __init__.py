#!/usr/bin/python
from helpers import *
from datetime import datetime, timedelta
import numpy as np

from controller.hamod import *

# Setup Vars
text_file_output = []
station_dict = {}


######################################
# Initializing Environment ~ MC/NM
######################################

car_count = 1
for station in STATION_MAPPING_INT.values():
    employees = EMPLOYEE_LIST[station]
    car_list = []
    emp_list = []
    for car in range(5):
        car_list.append(car_count)
        car_count += 1
    for emps in employees:
        emp_list.append(emps)
    # for i in range(4):
    #     emp_list.append(Employee(None, None, None))
    station_dict[station] = Station(station, car_list, emp_list)


# Add 4 employees to Station 0
emp_temp = []
for i in range(20):
    emp_temp.append(Employee(None, None, None))

station_dict[0].employee_list = emp_temp  # Should assign to HQ instead


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
# RoadNetwork['parking'] = np.array('file_from_matt_tsao.csv')
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
# c_r = 1


Parameters = {}
Parameters['pvCap'] = 4.
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

for time in range(70, len(cust_requests)):
    print("Time: {}".format(time))
    text_file_output.append("\nTime: {}".format(time))
    text_file_output.append('------------------------------------------------------')
    
    idle_vehicles = []
    idle_drivers = []

    vehicle_arrivals = np.zeros(shape=(len(station_dict), 12))
    driver_arrivals = np.zeros(shape=(len(station_dict), 12))

    customer_requests = cust_requests[time]

    errors = update(station_dict, customer_requests, time, driver_requests, pedestrian_requests)
    for station in station_dict:
        print('******************')
        print(station_dict[station].car_list)
        print('*******************')
    # Logging current state
    for station in sorted(station_dict):

        ######################################
        # Writing to text_file_output Files ~ NM
        ######################################

        text_file_output.append('\tStation: {}'.format(station))
        text_file_output.append('\t\tNumber of Idle Vehicles: {}'.format(len(station_dict[station].car_list)))
        text_file_output.append('\t\tAvailable Parking: {}'.format(50 - len(station_dict[station].car_list)))
        text_file_output.append('\t\tNumber of People En_Route: {}'.format(len(station_dict[station].get_en_route_list())))

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
                # if person.vehicle_id != None:
                #     if person.destination_time == i:
                #         if isinstance(person, Employee):
                #             driver_arrivals[station][i-time] += 1
                #
                #         vehicle_arrivals[station][i - time] += 1
                #         break
                if person.destination_time == i:
                    if isinstance(person, Employee):
                        driver_arrivals[station][i - time] += 1
                    if person.vehicle_id is not None:
                        vehicle_arrivals[station][i - time] += 1

                else:
                    break

    ######################################
    # Creating Forecast Dictionary ~ NM/MC
    ######################################

    Forecast = {
        # 'demand' : demand_forecast_parser(time), # ~ MC
        'demand': demand_forecast_parser_alt(time),
        'vehicle_arrivals': vehicle_arrivals,  # ~ NM
        'driver_arrivals': driver_arrivals,  # ~ NM
    }

    N = 58  # number of stations
    T = 12  # time step horizon
    T_init = int(np.ceil(T / 2))
    lam = 1/float(N)
    Forecast['demand'] = np.zeros((N, N, T))
    Forecast['demand'][:, :, 0:T_init] = np.random.poisson(lam, (N, N, T_init))
    Forecast['demand'] = np.random.poisson(lam, (N, N, T))

    # print("FORECAST")
    # for k, v in Forecast.items():
    #     print(k, v)

    ######################################
    # Creating State Dictionary ~ JS
    ######################################

    State = {
        'idleVehicles': np.array(idle_vehicles),
        'idleDrivers': np.array(idle_drivers),
        'privateVehicles': np.zeros((58, 1))
    }

    # print("idle drivers")
    # print(State['idleDrivers'])

    # Create controller if it doesn't already exist
    try:
        controller
    except:
        controller = MoDController(RoadNetwork)

    [tasks, controller_text_file_output] = controller.computerebalancing(Parameters, State, Forecast, Flags)

    # print("Tasks: ")
    # for k,v in tasks.items():
    #     print(k, v)
    #
    # print("\n\ntext_file_output:")
    # for c_text_file_output in controller_text_file_output:
    #     print(c_text_file_output)

    pedestrian_requests = tasks['driverRebalancingQueue']
    # for request in pedestrian_requests:
    #     print(request)
    vehicle_requests = tasks['vehicleRebalancingQueue']
    # print(pedestrian_requests)
    # print(vehicle_requests)

    text_file_output.append('Errors: {}'.format(errors))

    # driver_requests = format_instructions(text_file_output_requests)
    # customer_requests = format_instructions(text_file_output_requests)

######################################
# Tracking Errors / Summing Errors ~ JS
######################################

sum_station_no_park_errors = np.sum(no_park_errors, axis=0)  # no parking errors per station total
sum_station_no_car_cust_errors = np.sum(no_car_cust_errors, axis=0)  # no car available for custs errs per station total
sum_station_no_car_emp_errors = np.sum(no_car_emp_errors, axis=0)  # no car available for emps errs per station total

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