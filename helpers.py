from classes import *
from globals import *

def arrivals(arrival_list, time, cars, employees):
    for person in arrival_list:
        if person.get_destination_time() == time:

            arrival_list.remove(person)
            current_vehicle_id = person.get_vehicle_id()

            if current_vehicle_id is not None:
                cars.append(current_vehicle_id)

            if isinstance(person, Employee):
                person.reset()
                employees.append(person)
            else:
                del person

def assign_drivers(requests, time, cars, employee, station):
    for driver_request in requests:
        if driver_request[2] == time:
            try:
                current_car = cars.pop(0)

                current_employee = employee.pop(0)
                current_employee.update_status(driver_request, current_car)
                station[driver_request[1]].append_en_route_list(current_employee)
            except IndexError:
                # Save the Employee instructions
                print('Not enough cars for the employees')
                break
        else:
            break

def assign_pedestrians(requests, time, employee, station):
    for pedestrian_request in requests:
        if pedestrian_request[2] == time:
            current_employee = employee.pop(0)
            current_employee.update_status(pedestrian_request)
            station[pedestrian_request[1]].append_en_route_list(current_employee)
        else:
            break

def update_customer_list(requests, time, list):
    for customer_request in requests:
        if customer_request[2] == time:
            customer = Person(customer_request[0], customer_request[1], customer_request[0])
            list.append(customer)
        else:
                break

def assign_customers(list, cars, station_dictionary):
    for customer in list:
        try:
            current_car = cars.pop(0)

            current_customer = list.pop(0)
            current_customer.update_status(customer, current_car)
            station_dictionary[customer[1]].get_en_route_list().append(current_customer)
        except IndexError:
            print('Not enough cars for the customers')
            break

def check_every_minute(station_dict, driver_requests, pedestrian_requests, customer_requests, current_time):

    for station in station_dict:
        # NEED TO ADD Go through customer_requests to only have employees at this station

        # Grab information relevant to this loop and organize
        current_station = station_dict[station]
        current_car_list = current_station.get_car_list()
        employee_list = current_station.get_employee_list()
        customer_list = current_station.get_waiting_customers(True)
        en_route_list = current_station.get_en_route_list(True)

        # Loop Arrivals
        arrivals(en_route_list, current_time, current_car_list, employee_list)

        # Assign Employees
        assign_drivers(driver_requests, current_time, current_car_list, employee_list, current_station)
        assign_pedestrians(pedestrian_requests, current_time, employee_list, current_station)

        # Update Customer list and Assign Them
        update_customer_list(customer_requests, current_time, customer_list)
        assign_customers(customer_list, current_car_list, station_dict)

def format_instructions(current_time, matrix):
    requests = []

    try:
        for timestamp in matrix[current_time]:
            for row in timestamp:
                for number in row:
                    for __ in range(number):
                        requests.append(timestamp.index(row), row.index(number), current_time)
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

