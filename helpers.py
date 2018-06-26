from classes import *
from globals import *
import pandas as pd


def check_every_minute(station_dict, driver_requests, pedestrian_requests, customer_requests, current_time):

    for station in station_dict:
        # NEED TO ADD Go through customer_requests to only have employees at this station

        # Grab information relevant to this loop and organize
        current_station = station_dict[station]
        current_car_list = current_station.get_car_list()
        employee_list = current_station.get_employee_list()
        customer_list = current_station.get_waiting_customers()
        en_route_list = current_station.get_en_route_list()

        # Looping through arrivals
        for person in en_route_list:
            if person.get_destination_time() == current_time:

                en_route_list.remove(person)
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
            if driver_request[2] == current_time:
                try:
                    current_car = current_car_list.pop(0)

                    current_employee = employee_list.pop(0)
                    current_employee.update_status(driver_request, current_car)
                    station_dict[driver_request[1]].append_en_route_list(current_employee)
                except IndexError:
                    # Save the Employee instructions
                    print('Not enough cars for the employees')
                    break
            else:
                break

        # Looping through pedestrian requests and assigning them
        for pedestrian_request in pedestrian_requests:
            current_employee = employee_list.pop(0)
            current_employee.update_status(pedestrian_request)
            station_dict[pedestrian_request[1]].append_en_route_list(current_employee)

        # Appending customer requests
        for customer_request in customer_requests:
            customer_list.append(customer_request)

        # Sending out customers
        for customer in customer_list:
            try:
                current_car = current_car_list.pop(0)

                current_customer = customer_list.pop(0)
                current_customer.update_status(customer, current_car)
                station_dict[customer[1]].get_en_route_list().append(current_customer)
            except IndexError:
                    print('Not enough cars for the customers')
                    break


def instructions_every_five_minutes():
    pass


def create_dict(_list):
    _dict = {}
    for x in _list:
        _dict[x[0]] = Person(x[0], x[1])
    return _dict


def import_travel_times(filename):

    return pd.read_csv(filename)


def get_travel_time(time_graph, origin, destination):
    """
    little function for finding the value in a travel time graph
    :param time_graph: The padas Data Frame made for travel times
    :param origin: Where the car is traveling from
    :param destination: Where the car is going
    :return: Travel Time
    """
    return time_graph.loc[time_graph['station_id'] == origin][str(destination)].values[0]

