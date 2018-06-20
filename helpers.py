from classes import *
from globals import *

def checkEveryMinute(station_dict, employee_requests, customer_requests, current_time):

    for station in station_dict:
        curr_station = station_dict[station]
        # Loop 1
        for person in curr_station.get_en_route_list():
            curr_car_list = station.get_car_list()
            if person.get_desintation_time() == current_time:
                curr_vehicle_id = person.get_verichle_id()
                if curr_vehicle_id != None:
                    curr_car_list.append(person.get_verichle_id())
                if isinstance(Person(), Person):  # Is it a customer?
                    # get rid of person object
                    pass
                else:  # If employee then reset that employee and add to the employee queue
                    person.reset()
                    employee_list.append(person)


        # Loop 2
        for employee_request in station.get_employee_list():
            pass

        # Loop 3
        for customer_request in customer_requests:
            pass

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
    return GRAPH_VAR[origin][destination] + o_time
