#!/usr/bin/python
from classes import *
from helpers import *
from globals import *


# dicts for holding objects
EMPLOYEE_DICT = {}
STATION_DICT = {}
CAR_DICT = {}

# Create Objects
for station in range(len(STATION_LIST)):
    temp = []
    for car in CAR_LIST:
        if car[1] == station:
            temp.append(car[0])
        STATION_DICT[station] = Station(station, temp)

employee_dict = create_dict(EMPLOYEE_LIST)
car_dict = create_dict(CAR_LIST)


for num in range(1440):
    #checkEveryMinute(STATION_DICT)
    if (num % 60) == 0:
        instructionsEveryHour()