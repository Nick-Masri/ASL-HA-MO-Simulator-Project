from classes import *
from globals import *

def checkEveryMinute(station_dict, employee_requests, customer_requests, current_time):

    for station in station_dict:
        # Go through customer_requests to only have employees at this station

        current_station = station_dict[station]
        current_car_list = current_station.get_car_list()
        employee_list = current_station.get_employee_list()
        waiting_customers = current_station.get_waiting_list()

        # Loop 1
        enroute_list = current_station.get_enroute_list()
        for person in enroute_list:
            if person.get_desintation_time() == current_time:
                current_vehicle_id = person.get_vehicle_id()
                if current_vehicle_id is not None: # If person came in a car, add their car to the car list
                    current_car_list.append(person.get_verichle_id())

                if isinstance(Employee(), Person):  # Is it a employee?
                    person.reset()
                    employee_list.append(person)

                enroute_list.remove(person)  # Person is no longer enroute, remove from list


        # Loop 2
        employee_assignment_list = []
        for employee_request in employee_requests:
            employee_assignment_list.append(employee_list[employee_requests.index(employee_request)], employee_requests)

        # Loop 3
        for customer_request in customer_requests:
            waiting_customers.append(customer_request)


        request_list = employee_assignment_list + waiting_customers
        # Loop 4
        for request in (request_list):
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
