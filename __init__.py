#!/usr/bin/python
from helpers import *
from datetime import datetime, timedelta
import numpy as np

# Setup Vars
output = []
station_dict = {}

######################################
# Initializing Environment ~ MC
######################################

car_count = 1
for station in range(len(STATION_MAPPING_INT)):
    car_list = []
    emp_list = []
    for car in range(5):
        car_list.append(car_count)
        car_count += 1
    for emps in EMPLOYEE_LIST:
        if emps[1] == station:
            emp_list.append(emps[0])
    station_dict[station] = Station(station, car_list, emp_list)


######################################
# Creating Road Network Dictionary ~ NM
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
# RoadNetwork['pvTravelTimes'] = np.load('travel_times_matrix_car.npy')
# RoadNetwork['eTravelTimes'] = np.array('travel_times_matrix_car.csv')
# RoadNetwork['parking'] = np.array('file_from_matt_tsao.csv')

######################################
# Creating Parameters Dictionary ~ NM
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

######################################
# Creating Flags Dictionary ~ JS
######################################

# FLAGS = {'debugFlag': True is debugging, False if not, 'glpkFlag': True is using glpk, False is using cplex}
FLAGS = {'debugFlag': False, 'glpkFlag': False}

######################################
# Main Loop ~ NM
######################################

for time in range(len(CUST_REQUESTS)):
    print("Time: {}".format(time))
    output.append("\nTime: {}".format(time))
    output.append('------------------------------------------------------')
    
    iVehicles = []
    iDrivers = []

    vehicleArrivals = np.zeros(shape=(len(station_dict), 12))
    driverArrivals = np.zeros(shape=(len(station_dict), 12))
    
    driver_requests = format_instructions(time, load_instructions('driver'))
    pedestrian_requests = format_instructions(time, load_instructions('pedestrian'))
    customer_requests = CUST_REQUESTS[time]

    errors = update(station_dict, driver_requests, pedestrian_requests, customer_requests, time)
    print(errors)
    for station in station_dict:

        ######################################
        # Writing to Output Files ~ NM
        ######################################

        output.append('\tStation: {}'.format(station))
        output.append('\t\tNumber of Idle Vehicles: {}'.format(len(station_dict[station].car_list)))
        output.append('\t\tAvailable Parking: {}'.format(50 - len(station_dict[station].car_list)))
        output.append('\t\tNumber of People En_Route: {}'.format(len(station_dict[station].get_en_route_list())))

        ############################################
        # Setting Up Idle Vehicles and Drivers ~ JS
        ############################################

        iVehicles.append(len(station_dict[station].car_list))
        iDrivers.append(len(station_dict[station].employee_list))

        ########################################
        # Updating Vehicle/Driver Arrivals ~ NM
        ########################################

        for person in station_dict[station].get_en_route_list(True):
            for i in range(time, time + 12):
                if person.vehicle_id != None:
                    if person.destination_time == i:
                        if isinstance(person, Employee):
                            driverArrivals[station][i-time] += 1

                        vehicleArrivals[station][i - time] += 1
                        break
                else:
                    break

    ######################################
    # Creating Forecast Dictionary ~ NM/MC
    ######################################

    Forecast = {
        'demand' : demand_forecast_parser(time), # ~ MC
        'vehicleArrivals': np.array(vehicleArrivals), # ~ NM
        'driverArrivals' : np.array(driverArrivals), # ~ NM
    }

    ######################################
    # Creating State Dictionary ~ JS
    ######################################

    State = {
        'idleVehicles': np.array(iVehicles),
        'idleDrivers': np.array(iDrivers),
        'privateVehicles': 0
    }

    output.append('Errors: {}'.format(errors))

######################################
# Tracking Errors / Summing Errors ~ JS
######################################

sumStationNoParkErrors = np.sum(noParkErrors, axis = 0) # no parking errors per station total
sumStationNoCarErrors = np.sum(noCarErrors, axis = 0) # no car available errors per station total

sumTimeNoParkErrors = np.sum(noParkErrors, axis = 1) # no parking errors per time total
sumTimeNoCarErrors = np.sum(noCarErrors, axis = 1) # no car available errors per time total

######################################
# Writing to Output File ~ NM
######################################

output_file = open('output.txt', 'w')

for item in output:
  output_file.write("%s\n" % item)

output_file.close()