#!/usr/bin/python
from helpers import *

# Setup Vars
output = []
station_dict = {}

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

for time in range(len(CUST_REQUEST)):
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
        iVehicles.append(len(station_dict[station].get_car_list()))
        iDrivers.append(len(station_dict[station].get_employee_list()))

    # station = 5
    # output.append('\tStation: {}'.format(station))
    # output.append('\t\tNumber of Idle Vehicles: {}'.format(len(station_dict[station].get_car_list())))
    # output.append('\t\tAvailable Parking: {}'.format(50 - len(station_dict[station].get_car_list())))
    # output.append('\t\tNumber of People En_Route: {}'.format(len(station_dict[station].get_en_route_list())))
    
    STATE = {'idleVehicles': iVehicles, 'idleDrivers': iDrivers, 'privateVehicles': 0}
    print(STATE)
    
    output.append('Errors: {}'.format(errors))
    

output_file = open('output.txt', 'w')

for item in output:
  output_file.write("%s\n" % item)

output_file.close()

request_file = open('request_file.txt', 'w')

for x in CUST_REQUESTS:
    request_file.write('{}\n'.format(x))

request_file.close()


