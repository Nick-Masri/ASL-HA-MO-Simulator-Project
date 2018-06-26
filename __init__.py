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

# holds people in (o, d, ot) form
person_list = []


print(CAR_TRAVEL_TIMES)
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

    print(station_dict.get(station).get_car_list())
    #print(station_dict.get(station).get_employee_list())

# Turning Person Matrix to (o, d, ot) form
for origin in PERSON_LIST:
    for destination in origin:
        person_list.append(Person(origin[0]+1, destination+1, 0))
#print(person_list[0].get_origin())

#Place Person objects into repspective station waiting lists
for station in station_dict:
    for customer in person_list:
        if customer.get_origin() == station:
            station_dict[station].append_waiting_customers(customer)

# Full loop of 24 hours of checks


for time in range(1440):
    if (time % 5) == 0:
        instructions_every_five_minutes()
    check_every_minute(station_dict, driver_requests, pedestrian_requests, customer_requests, time)

