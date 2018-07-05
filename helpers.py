from classes import *
from globals import *


def arrivals(arrival_list, time, cars, employees, station):
    while len(arrival_list) > 0:
        person = arrival_list[0]
        if person.get_destination_time() == time: # there is an error at time = 0

            arrival_list.remove(person)
            station.get_en_route_list().remove(person)
            current_vehicle_id = person.get_vehicle_id()

            if current_vehicle_id is not None:
                cars.append(current_vehicle_id)

            if isinstance(person, Employee):
                person.reset()
                employees.append(person)
            else:
                del person

        else:
            break


def assign_drivers(requests, time, cars, employee, station):
    for driver_request in requests:
        # try:
        #     current_car = cars.pop(0)
        #
        #     current_employee = employee.pop(0)
        #     current_employee.update_status(driver_request, current_car)
        #     station[driver_request[1]].append_en_route_list(current_employee)
        # except IndexError:
        #     # Save the Employee instructions
        #     print('Not enough cars for the employees')
        #     break
        break


def assign_pedestrians(requests, time, employee, station):
    for pedestrian_request in requests:
    #     current_employee = employee.pop(0)
    #     current_employee.update_status(pedestrian_request)
    #     station[pedestrian_request[1]].append_en_route_list(current_employee)
        break


def update_customer_list(requests, time, cust_list):
    customer = Person(requests[0][0], requests[0][1], time)
    cust_list.append(customer)



def assign_customers(customer_list, cars, station_dictionary, errors):

    customer = customer_list[0]
    try:
        current_car = cars.pop(0)
        current_customer = customer_list.pop(0)
        current_customer.update_status(customer, current_car)
        station_dictionary[customer.get_destination()].append_en_route_list(current_customer)
    except IndexError:
        errors.append('No car for customer at Station Number {}'.format(customer.get_origin()))



def update(station_dict, driver_requests, pedestrian_requests, customer_requests, current_time):
    errors = []

    for station in station_dict:

        # For future efficiency check to see if there are any requests before doing all this work.

        # Grab information relevant to this loop and organize
        current_station = station_dict[station]
        current_car_list = current_station.get_car_list()
        employee_list = current_station.get_employee_list()
        customer_list = current_station.get_waiting_customers(True)
        en_route_list = current_station.get_en_route_list(True)

        # Loop Arrivals
        arrivals(en_route_list, current_time, current_car_list, employee_list, current_station)

        # Check for Errors
        overload = 50 - (len(current_station.get_car_list()) + len(current_station.get_en_route_list()))

        if overload < 0:
            errors.append("Station {0}  will have {1} more cars than it can allow".format(current_station, -overload))

        # Assign Employees
        # assign_drivers(driver_requests, current_time, current_car_list, employee_list, current_station)
        # assign_pedestrians(pedestrian_requests, current_time, employee_list, current_station)

        # Update Customer list and Assign Them
        if len(customer_requests) > 0:
            if customer_requests[0][0] == station:
                update_customer_list(customer_requests, current_time, customer_list)  # add to station cust waiting list
                assign_customers(customer_list, current_car_list, station_dict, errors)  # assigns customers to cars if available
    return errors


# Not currently in use
def format_instructions(current_time, matrix):
    requests = []

    try:
        for timestamp in matrix[current_time]:
            for row in timestamp:
                for number in row:
                    for __ in range(number):
                        requests.append([timestamp.index(row), row.index(number), current_time])
    except IndexError:
        print("No Requests")

    return requests


def load_instructions(selector):
    if selector == 'driver':
        return DRIVER_INSTRUCTIONS
    if selector == 'pedestrian':
        return PEDESTRIAN_INSTRUCTIONS
    if selector == 'customer':
        return CUSTOMER_INSTRUCTIONS


