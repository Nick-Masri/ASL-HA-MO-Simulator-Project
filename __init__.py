#!/usr/bin/python
from helpers import *

# Setup Vars
station_dict = {}

# Request Matrices
driver_matrix = []
pedestrian_matrix = []
customer_matrix = []


# Full loop of 24 hours of checks


for time in range(1440):
    if (time % 5) == 0:
        driver_requests = instructions_every_five_minutes(time, driver_matrix)
        pedestrian_requests = instructions_every_five_minutes(time, pedestrian_matrix)
        customer_requests = instructions_every_five_minutes(time, customer_matrix)
    check_every_minute(station_dict, driver_requests, pedestrian_requests, customer_requests, time)