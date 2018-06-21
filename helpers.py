from classes import *
from globals import *


def checkEveryMinute(station_dict, driver_requests, pedestrian_requests, customer_requests, current_time):

    for station in station_dict:
        # Go through customer_requests to only have employees at this station

        current_station = station_dict[station]
        current_car_list = current_station.get_car_list()
        employee_list = current_station.get_employee_list()
        customer_list = current_station.get_waiting_list()

        # Loop 1
        enroute_list = current_station.get_enroute_list()
        for person in enroute_list:
            if person.get_destination_time() == current_time:
                current_vehicle_id = person.get_vehicle_id()
                if current_vehicle_id is not None:  # If person came in a car, add their car to the car list
                    current_car_list.append(current_vehicle_id)

                if isinstance(person, Employee):  # Is it a employee?
                    person.reset()
                    employee_list.append(person)
                # For memory concerns should we delete the a customer object that after they return?
                enroute_list.remove(person)  # Person is no longer enroute, remove from list

        ## This whole section needs some functions, there's a lot of repeated logic here.
        ## Do we need to update current_location? Is it a duplicate?

        # Assign driver requests to employees currently at the station
        # Sends drivers out right away
        for driver_request in driver_requests:

            current_employee = employee_list.pop(0)  # Grabs an employee and removes from current station list
            current_car = current_car_list.pop(0)  # Grabs a car and removes from the current station list
            # do we need to change the current_position?

            current_employee.update_status(driver_request, current_car)  # New function that takes care of the lines above
            # Move the employee to the destination enroute list
            station_dict[driver_request[1]].get_enroute_list().append(current_employee)

        # Send out Pedestrians
        for pedestrian_request in pedestrian_requests:
            current_employee.update_status(pedestrian_request)
            # Move the employee to the destination enroute list
            station_dict[pedestrian_request[1]].get_enroute_list().append(current_employee)

        # Add customer requests to the customer wait list
        for customer_request in customer_requests:
            customer_list.append(customer_request)
        
        # Send out customers
        for customer_request in customer_requests:
            current_customer = customer_list.pop(0)  # Grabs an customer and removes from current station list
            # current_customer.change_origin(customer_request[0])  # Set origin
            # current_customer.change_destination(customer_request[1])  # Set departure
            # current_customer.change_origin_time(customer_request[2])  # Set origin time

            current_customer.update_status(customer_request)
            # Move the customer to the destination enroute list
            station_dict[customer_request[1]].get_enroute_list().append(current_customer)


def instructionsEveryHour():
    pass


def create_dict(_list):
    _dict = {}
    for x in _list:
        _dict[x[0]] = Person(x[0], x[1])
    return _dict

def calc_d_time(origin, destination, o_time):
    return GRAPH_VAR[origin][destination] + o_time
