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

for time in range(len(CUST_REQUESTS)):
    print("Time: {}".format(time))
    output.append("Time: {}".format(time))

    driver_requests = format_instructions(time, load_instructions('driver'))
    pedestrian_requests = format_instructions(time, load_instructions('pedestrian'))
    customer_requests = CUST_REQUESTS[time]
    update(station_dict, driver_requests, pedestrian_requests, customer_requests, time)

    for station in station_dict:
        output.append('\tStation: {}'.format(station))
        output.append('\t\tNumber of Idle Vehicles: {}'.format(len(station_dict[station].get_car_list())))
        output.append('\t\tAvailable Parking: {}'.format(50 - len(station_dict[station].get_car_list())))
        output.append('\t\tNumber of People En_Route: {}'.format(len(station_dict[station].get_en_route_list())))




thefile = open('output.txt', 'w')

for item in output:
  thefile.write("%s\n" % item)