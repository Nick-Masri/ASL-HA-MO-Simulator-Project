#!/usr/bin/python
from classes import *
from helpers import *
from globals import *

# Setup Vars
station_dict = {}

# Requests
driver_requests = []
pedestrian_requests = []
customer_requests = []

# Create Objects
for station in range(1, len(STATION_LIST)):
    temp1 = []
    temp2 = []
    for cars in CAR_LIST:
        if cars[1] == station:
            temp1.append(cars[0])
    for emps in EMPLOYEE_LIST:
        if emps[1] == station:
            temp2.append(emps[0])
    station_dict[station] = Station(station, temp1, temp2)
    
    #print(STATION_DICT.get(station).get_car_list())
    #print(STATION_DICT.get(station).get_employee_list())

# Full loop of 24 hours of checks


for time in range(1440):

    check_every_minute(station_dict, driver_requests, pedestrian_requests, customer_requests, time)
    if (time % 5) == 0:
        instructions_every_five_minutes()