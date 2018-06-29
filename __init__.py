#!/usr/bin/python
from helpers import *

# Setup Vars
station_dict = {}


for station in STATION_MAPPING_INT:
    temp1 = []
    temp2 = []
    for cars in CAR_LIST:
        if cars[1] == station:
            temp1.append(cars[0])
    for emps in EMPLOYEE_LIST:
        if emps[1] == station:
            temp2.append(emps[0])
    station_dict[station] = Station(station, temp1, temp2)

# Full loop of 24 hours of checks
for time in range(len(CUST_REQUESTS)):
    driver_requests = format_instructions(time, load_instructions('driver'))
    pedestrian_requests = format_instructions(time, load_instructions('pedestrian'))
    customer_requests = CUST_REQUESTS[time]
    update(station_dict, driver_requests, pedestrian_requests, customer_requests, time)
    

