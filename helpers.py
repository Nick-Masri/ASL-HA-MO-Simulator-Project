from classes import *
from globals import *

def checkEveryMinute(station_dict, employee_requests, customer_requests):

    for station in station_dict:
        # Go through employee_requests to only have employees at this station
        # Go through customer_requests to only have employees at this station

        curr_station = station_dict[station]

        employee_list = curr_station.get_employee_list()
        customer_list = curr_station.get_customer_list()

        # Loop 1
        for person in curr_station.get_en_route_list():
            pass

        # Loop 2
        for employee_request in employee_requests:
            station.assign_employee(employee_list[employee_requests.index(employee_request)], employee_request)

        # Loop 3
        for customer_request in customer_requests:
            customer_list.append(customer_request)

        # Loop 4
        for request in (station.get_request_list()):
            pass

def instructionsEveryHour():
    pass

def create_dict(_list):
    _dict = {}
    for x in _list:
        _dict[x[0]] = Asset(x[0], x[1])
    return _dict

def calc_d_time(origin, destination, o_time):
    return GRAPH_var[origin][destination] + o_time
