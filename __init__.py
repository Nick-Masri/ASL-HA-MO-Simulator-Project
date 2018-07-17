#!/usr/bin/python
from helpers import *
from datetime import datetime, timedelta
import numpy as np

from controller.hamod import *

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
# Creating Road Network Dictionary ~ NM and MC
######################################

neighbor_list = []
num_of_stations = len(STATION_MAPPING_INT)

# Indexed 1 (assumes logical indices)
for station in range(1,num_of_stations+1):
    # Excluding the current station from the list of neighbors
    # lst = [i for i in range(1,num_of_stations+1) if i != station]
    # neighbor_list.append(np.asarray(lst).reshape((1, num_of_stations-1)))

    lst = [i for i in range(1,num_of_stations+1)]
    neighbor_list.append(np.asarray(lst).reshape((1,num_of_stations)))


print("NEIGHBOR")
print(len(neighbor_list[0][0]))

RoadNetwork = {}
RoadNetwork['roadGraph'] = neighbor_list
RoadNetwork['travelTimes'] = HAMO_TRAVEL_TIMES
RoadNetwork['driverTravelTimes'] = PEDESTRIAN_TRAVEL_TIMES
RoadNetwork['pvTravelTimes'] = CAR_TRAVEL_TIMES
RoadNetwork['cTravelTimes'] = CAR_TRAVEL_TIMES  # Assuming that customer travel time = CAR travel time
# RoadNetwork['parking'] = np.array('file_from_matt_tsao.csv')
RoadNetwork['parking'] = np.array([10 for i in range(58)])


print('ROADNETWORK')
for k, v in RoadNetwork.items():
    try:
        print(k, v.shape)
    except:
        print(k, v)


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
Parameters['lostDemandCost'] = c_d
Parameters['thor'] = float(int(horizon.seconds / timestepsize.seconds))
for k, v in Parameters.items():
    print(k, type(v))

######################################
# Creating Flags Dictionary ~ JS
######################################

# FLAGS = {'debugFlag': True is debugging, False if not, 'glpkFlag': True is using glpk, False is using cplex}
Flags = {'debugFlag': False, 'glpkFlag': False}

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
    # print(errors)
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
        'vehicleArrivals': vehicleArrivals, # ~ NM
        'driverArrivals' : driverArrivals, # ~ NM
    }
    print("FORECAST")
    for k, v in Forecast.items():
        print(k, v.shape)

    ######################################
    # Creating State Dictionary ~ JS
    ######################################

    State = {
        'idleVehicles': np.array(iVehicles),
        'idleDrivers': np.array(iDrivers),
        'privateVehicles': np.zeros((58,1))
    }

    controller = MoDController(RoadNetwork)
    [tasks, output] = controller.computerebalancing(Parameters, State, Forecast, Flags)
    print(tasks)
    output.append('Errors: {}'.format(errors))
    break

######################################
# Tracking Errors / Summing Errors ~ JS
######################################

sumStationNoParkErrors = np.sum(noParkErrors, axis = 0) # no parking errors per station total
sumStationNoCarCustErrors = np.sum(noCarCustErrors, axis = 0) # no car available for customers errors per station total
sumStationNoCarEmpErrors = np.sum(noCarEmpErrors, axis = 0) # no car available for employees errors per station total

sumTimeNoParkErrors = np.sum(noParkErrors, axis = 1) # no parking errors per time total
sumTimeNoCarCustErrors = np.sum(noCarCustErrors, axis = 1) # no car available for customers errors per time total
sumTimeNoCarEmpErrors = np.sum(noCarEmpErrors, axis = 1) # no car available for employees errors per time total

######################################
# Writing to Output File ~ NM
######################################

output_file = open('output.txt', 'w')

for item in output:
  output_file.write("%s\n" % item)

output_file.close()