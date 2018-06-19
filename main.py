#!/usr/bin/python
from functions import *

# Initializing Time
time = [0, 0, 0]  # Time Starts at 0

# Initializing Setup Variables (Random rn)
<<<<<<< HEAD
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

=======
employee_list = [[1, 2], [2, 5], [3, 7], [4, 10]]
car_list = [[1, 1], [2, 2], [3, 2], [4, 4], [5, 4], [6, 6], [7, 9], [8, 10]]
map = [[0, 5, 8, 11, 13, 13, 12, 11, 8, 5], [5, 0, 5, 8, 11, 13, 13, 12, 11, 8], [8, 5, 0, 5, 8, 11, 13, 13, 12, 11],
       [11, 8, 5, 0, 5, 8, 11, 13, 13, 12], [12, 11, 8, 5, 0, 5, 8, 11, 13, 13],
       [13, 12, 11, 8, 5, 0, 5, 8, 11, 13], [13, 13, 12, 11, 8, 5, 0, 5, 8, 11], [11, 13, 13, 12, 11, 8, 5, 0, 5, 8],
       [8, 11, 13, 13, 12, 11, 8, 5, 0, 5], [5, 8, 11, 13, 13, 12, 11, 8, 5, 0]]
>>>>>>> 34ae4dd... Added looping every minute to go for 24 hours
station_list = []
employee_dict = {}

for i in range(1, 11):
    station_list.append((i))
# Calling the Functions

for x in employee_list:
    employee_dict[x[0]] = Employee(x[0], x[1])

<<<<<<< HEAD
print(employee_dict)
=======
>>>>>>> 34ae4dd... Added looping every minute to go for 24 hours

def checkEveryMinute():
    pass

def instructionsEveryHour():
    pass

for _ in range(24):
    for _ in range(59):
        time[1] += 1

        print(time)
    time[1] = 0
    time[0] += 1

<<<<<<< HEAD
    time[0] += 01
'''

'''
from functions.py import *

for current_time in :
    For loop through the time of day (for current_time in day_time:)
        For loop through the cars
            Check if destination_time == current_time
                Change status of employee from rebalancing to idle
            Check if any of the employees are idle:
'''
=======

    print(time)

>>>>>>> 34ae4dd... Added looping every minute to go for 24 hours
