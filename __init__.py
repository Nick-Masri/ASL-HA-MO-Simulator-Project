#!/usr/bin/python
from helpers import *

# Setup Vars
station_dict = {}



for employee in EMPLOYEE_LIST:













# Request Matrices
driver_matrix = []
pedestrian_matrix = []
customer_matrix = []

# Full loop of 24 hours of checks
for time in range(1440):
    if (time % 5) == 0 or (time == 0):
        driver_requests = format_instructions(time, load_instructions('driver'))
        pedestrian_requests = format_instructions(time, load_instructions('pedestrian'))
        customer_requests = format_instructions(time, load_instructions('customer'))
    check_every_minute(station_dict, driver_requests, pedestrian_requests, customer_requests, time)