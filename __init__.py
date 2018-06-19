#!/usr/bin/python
from classes import *
from helpers import *

GRAPH = [[0,5,8,11,13,13,12,11,8,5],  # needs to be 50x50 eventually
         [5,0,5,8,11,13,13,12,11,8],
         [8,5,0,5,8,11,13,13,12,11],
         [11,8,5,0,5,8,11,13,13,12],
         [12,11,8,5,0,5,8,11,13,13],
         [13,12,11,8,5,0,5,8,11,13],
         [13,13,12,11,8,5,0,5,8,11],
         [11,13,13,12,11,8,5,0,5,8],
         [8,11,13,13,12,11,8,5,0,5],
         [5,8,11,13,13,12,11,8,5,0]]

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

print(station_dict)
for di in station_dict:
    print(station_dict[di].get_available_cars())


employee_dict = create_dict(employee_list)
car_dict = create_dict(car_list)

for num in range(1440):
    checkEveryMinute()
    if (num % 60) == 0:
        instructionsEveryHour()