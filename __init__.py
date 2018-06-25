#!/usr/bin/python
from helpers import *

# Setup Vars
station_dict = {}

for employee in EMPLOYEE_LIST:
    pass

for station in range(1, len(GRAPH_VAR)+1):
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
for time in range(1440):
    if (time % 5) == 0 or (time == 0):
        driver_requests = format_instructions(time, load_instructions('driver'))
        pedestrian_requests = format_instructions(time, load_instructions('pedestrian'))
        customer_requests = format_instructions(time, load_instructions('customer'))
    check_every_minute(station_dict, driver_requests, pedestrian_requests, customer_requests, time)