#!/usr/bin/python
from classes import *
from helpers import *
import globals


# Initializing Time
time = [0, 0, 0]  # Time Starts at 0

# Initializing Setup Variables (Random rn)
employee_list = [[1, 2], 
                 [2, 5], 
                 [3, 7], 
                 [4, 10]]

car_list = [[1, 1], 
            [2, 2], 
            [3, 2], 
            [4, 4], 
            [5, 4], 
            [6, 6], 
            [7, 9], 
            [8,10]]

station_list = [num for num in range(11)]

# dicts for holding objects
employee_dict = {}
station_dict = {}
car_dict = {}

# Create Objects
for station in range(len(station_list)):
    temp = []
    for car in car_list:
        if car[1] == station:
            temp.append(car[0])
    station_dict[station] = Station(station, temp)


employee_dict = create_dict(employee_list)
car_dict = create_dict(car_list)

for num in range(1440):
    checkEveryMinute()
    if (num % 60) == 0:
        instructionsEveryHour()