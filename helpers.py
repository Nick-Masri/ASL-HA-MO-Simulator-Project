from classes import *
from globals import *


def checkEveryMinute(station_dict, driver_requests, pedestrian_requests, customer_requests, current_time):

    for station in station_dict:
        # Go through customer_requests to only have employees at this station

        current_station = station_dict[station]
        current_car_list = current_station.get_car_list()
        employee_list = current_station.get_employee_list()
        customer_list = current_station.get_waiting_list()
        enroute_list = current_station.get_enroute_list()

        # Looping through arrivals
        for person in enroute_list:
            if person.get_destination_time() == current_time:

                enroute_list.remove(person)
                current_vehicle_id = person.get_vehicle_id()

                if current_vehicle_id is not None:
                    current_car_list.append(current_vehicle_id)

                if isinstance(person, Employee):
                    person.reset()
                    employee_list.append(person)
                else:
                    del person

        # Looping through driver requests and assigning them
        for driver_request in driver_requests:
            try:
                current_car = current_car_list.pop(0)

                current_employee = employee_list.pop(0)
                current_employee.update_status(driver_request, current_car)
                station_dict[driver_request[1]].append_enroute_list(current_employee)
            except IndexError:
                # Save the Employee_list
                break


        # Looping through pedestrian requests and assigning them
        for pedestrian_request in pedestrian_requests:
            current_employee = employee_list.pop(0)
            current_employee.update_status(pedestrian_request)
            station_dict[pedestrian_request[1]].append_enroute_list(current_employee)

        # Appending customer requests
        for customer_request in customer_requests:
            customer_list.append(customer_request)

        # Sending out customers
        for customer_request in customer_requests:
            try:
                current_car = current_car_list.pop(0)

                current_customer = customer_list.pop(0)
                current_customer.update_status(customer_request, current_car)
                station_dict[customer_request[1]].get_enroute_list().append(current_customer)
            except IndexError:
                    break



def instructionsEveryHour():
    pass


def create_dict(_list):
    _dict = {}
    for x in _list:
        _dict[x[0]] = Person(x[0], x[1])
    return _dict

def calc_d_time(origin, destination, o_time):
    return GRAPH_VAR[origin][destination] + o_time
