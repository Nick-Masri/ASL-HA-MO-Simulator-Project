#!/usr/bin/python
from functions import *

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

map = [[0,5,8,11,13,13,12,11,8,5], # needs to be 50x50
       [5,0,5,8,11,13,13,12,11,8], 
       [8,5,0,5,8,11,13,13,12,11], 
       [11,8,5,0,5,8,11,13,13,12], 
       [12,11,8,5,0,5,8,11,13,13], 
       [13,12,11,8,5,0,5,8,11,13], 
       [13,13,12,11,8,5,0,5,8,11], 
       [11,13,13,12,11,8,5,0,5,8], 
       [8,11,13,13,12,11,8,5,0,5], 
       [5,8,11,13,13,12,11,8,5,0]]


station_list = []
employee_dict = {}

for i in range(1, 11):
    station_list.append((i))
# Calling the Functions

for x in employee_list:
    employee_dict[x[0]] = Employee(x[0], x[1])


def checkEveryMinute():
    pass

def instructionsEveryHour():
    pass

for _ in range(24):
    for _ in range(59):
        time[1] += 1
        checkEveryMinute()
        #print(time)
    time[1] = 0
    time[0] += 1
    instructionsEveryHour()
    #print time