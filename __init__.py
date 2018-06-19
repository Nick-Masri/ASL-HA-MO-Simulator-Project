#!/usr/bin/python
from classes import *
from helpers import *

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

# dicts for holding objects
employee_dict = {}
station_dict = {}
car_dict = {}

# Create Objects
for station in range(len(station_list)):
    station_dict[station] = Station(station)

employee_dict = CreateDict(employee_list)
car_dict = CreateDict(car_list)

for num in range(1440):
    checkEveryMinute()
    if (num % 60) == 0:
        instructionsEveryHour()