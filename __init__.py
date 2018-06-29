#!/usr/bin/python
from helpers import *

# Setup Vars
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

state = []
# Full loop of 24 hours of checks
for time in range(len(CUST_REQUESTS)):
    print("Time: {}".format(time))
    driver_requests = format_instructions(time, load_instructions('driver'))
    pedestrian_requests = format_instructions(time, load_instructions('pedestrian'))
    customer_requests = CUST_REQUESTS[time]
    temp = update(station_dict, driver_requests, pedestrian_requests, customer_requests, time)
    temp_station = {}
    stations = temp[0]  # The station dict
    for station in stations:
        temp_station[station] = {'Cars': stations[station].get_car_list(),
                                 'Waiting Customers': len(stations[station].get_employee_list()),
                                 # There's clearly an issue here. The enroute list is always length: 58!!
                                 'en_route_list': len(stations[station].get_en_route_list()),
                                 'self.request_list': len(stations[station].get_request_list())}
    print(temp_station)
    break


    

