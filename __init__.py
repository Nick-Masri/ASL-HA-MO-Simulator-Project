#!/usr/bin/python
from helpers import *
from datetime import datetime, timedelta
import numpy as np

# Setup Vars
output = []
station_dict = {}

# Controller Inputs

# FLAGS = {'debugFlag': True is debugging, False if not, 'glpkFlag': True is using glpk, False is using cplex }
FLAGS = {'debugFlag': False, 'glpkFlag': False}

car_count = 1
for station in STATION_MAPPING_INT:
    car_list = []
    emp_list = []
    for car in range(5):
        car_list.append(car_count)
        car_count += 1
    for emps in EMPLOYEE_LIST:
        if emps[1] == station:
            emp_list.append(emps[0])
    station_dict[station] = Station(station, car_list, emp_list)

for time in range(len(CUST_REQUESTS)):
    print("Time: {}".format(time))
    output.append("\nTime: {}".format(time))
    output.append('------------------------------------------------------')
    
    iVehicles = []
    iDrivers = []

    driver_requests = format_instructions(time, load_instructions('driver'))
    pedestrian_requests = format_instructions(time, load_instructions('pedestrian'))
    customer_requests = CUST_REQUESTS[time]

    errors = update(station_dict, driver_requests, pedestrian_requests, customer_requests, time)

    for station in station_dict:
        output.append('\tStation: {}'.format(station))
        output.append('\t\tNumber of Idle Vehicles: {}'.format(len(station_dict[station].get_car_list())))
        output.append('\t\tAvailable Parking: {}'.format(50 - len(station_dict[station].get_car_list())))
        output.append('\t\tNumber of People En_Route: {}'.format(len(station_dict[station].get_en_route_list())))
        
        # STATE lists
        iVehicles.append(len(station_dict[station].get_car_list()))
        iDrivers.append(len(station_dict[station].get_employee_list()))

    # station = 5
    # output.append('\tStation: {}'.format(station))
    # output.append('\t\tNumber of Idle Vehicles: {}'.format(len(station_dict[station].get_car_list())))
    # output.append('\t\tAvailable Parking: {}'.format(50 - len(station_dict[station].get_car_list())))
    # output.append('\t\tNumber of People En_Route: {}'.format(len(station_dict[station].get_en_route_list())))
    
    State = {
            'idleVehicles': np.array(iVehicles), 
            'idleDrivers': np.array(iDrivers), 
            'privateVehicles': 0
            }
    

    
    output.append('Errors: {}'.format(errors))


print(State)

output_file = open('output.txt', 'w')

for item in output:
  output_file.write("%s\n" % item)

output_file.close()

request_file = open('request_file.txt', 'w')

for x in CUST_REQUESTS:
    request_file.write('{}\n'.format(x))

request_file.close()

######################################
# Creating Road Network Dictionary
######################################

neighbor_list = []

for station in STATION_MAPPING_INT:
    neighboring_stations = []
    for i in range(len(STATION_MAPPING_INT)):
        if i != station:
            neighboring_stations.append(i)
    neighbor_list.append(neighboring_stations)

RoadNetwork = {}
RoadNetwork['roadGraph'] = neighbor_list
# RoadNetwork['travelTimes'] = np.array('travel_times_matrix_hamo.csv')
# RoadNetwork['driverTravelTimes'] =  np.array('travel_times_matrix_walk.csv')
# RoadNetwork['pvTravelTimes'] = np.array('travel_times_matrix_car.csv')
# RoadNetwork['eTravelTimes'] = np.array('travel_times_matrix_car.csv')
# RoadNetwork['parking'] = np.array('file_from_matt_tsao.csv')


######################################
# Creating Parameters Dictionary
######################################

dt = 5 # minutes
timestepsize = timedelta(0, 60*dt) # in seconds
horizon = timedelta(0, 12*60*dt) # in seconds
thor = int(horizon.seconds / timestepsize.seconds)
c_d = 10000.
c_r = (1. / thor) * 0.0001 * 24. * c_d

Parameters = {}
Parameters['pvCap'] = 4.
Parameters['driverRebalancingCost'] = c_r
Parameters['vehicleRebalancingCost'] = c_r
Parameters['pvRebalancingCost'] = c_r
Parameters['lostDemandCost'] =  c_d
Parameters['thor'] = float(int(horizon.seconds / timestepsize.seconds))