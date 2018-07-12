from classes import *
from globals import *

######################################
# Instantiating Error Arrays ~ JS
######################################

noCarErrors = np.zeros(shape=(2880, 58))
noParkErrors = np.zeros(shape=(2880, 58))

######################################
# Creating Functions For Update ~ NM
######################################

def arrivals(arrival_list, time, cars, employees, station):
    while len(arrival_list) > 0:
        person = arrival_list[0]
        if person.destination_time == time: # there is an error at time = 0
            arrival_list.remove(person)
            station.get_en_route_list().remove(person)
            current_vehicle_id = person.vehicle_id
            if current_vehicle_id is not None:
                cars.append(current_vehicle_id)
            if isinstance(person, Employee):
                person.reset()
                employees.append(person)
            else:
                del person
        else:
            break


def assign_drivers(cars, employee_list, station_dictionary, errors):
    while len(employee_list) > 0:
        driver = employee_list[0]
        try:
            current_car = cars.pop(0)
            current_customer = employee_list.pop(0)
            current_customer.update_status(driver, current_car)
            station_dictionary[driver.destination].append_en_route_list(current_customer)
        except IndexError:
            errors.append('No car for customer at Station Number {}'.format(driver.origin))
            break


def assign_pedestrians(employee_list, station_dictionary):
    while len(employee_list) > 0:
        current_ped = employee_list.pop(0)
        station_dictionary[current_ped.destination].append_en_route_list(current_ped)



def update_customer_list(requests, time, cust_list):
    customer = Person(requests[0], requests[1], time)
    cust_list.append(customer)



def assign_customers(customer_list, cars, station_dictionary, errors, current_time):
    while len(customer_list) > 0:
        customer = customer_list[0]
        try:
            current_car = cars.pop(0)
            current_customer = customer_list.pop(0)
            current_customer.update_status(customer, current_car)
            station_dictionary[customer.destination].append_en_route_list(current_customer)
        except IndexError:
            errors.append('No car for customer at Station Number {}'.format(customer.origin))
            noCarErrors[current_time, customer.origin] += 1
            break



######################################
# Update Loop ~ NM
######################################

def update(station_dict, driver_requests, pedestrian_requests, customer_requests, current_time):
    errors = []
    for station in station_dict:
        # For future efficiency check to see if there are any requests before doing all this work.

        # Grab information relevant to this loop and organize
        current_station = station_dict[station]
        current_car_list = current_station.car_list
        employee_list = current_station.employee_list
        customer_list = current_station.get_waiting_customers(True)
        en_route_list = current_station.get_en_route_list(True)

        # Loop Arrivals
        arrivals(en_route_list, current_time, current_car_list, employee_list, current_station)

        # Check for Errors
        overload = 50 - (len(current_station.car_list) + len(current_station.get_en_route_list()))

        if overload < 0:
            errors.append("Station {0}  will have {1} more cars than it can allow".format(current_station, -overload))
            noParkErrors[current_time, current_station] += 1

        # Update Customer list and Assign Them
        for customer_request in customer_requests:
            if customer_request[0] == station:
                update_customer_list(customer_request, current_time, customer_list)  # add to station cust waiting list
        assign_customers(customer_list, current_car_list, station_dict, errors, current_time)  # assigns customers to cars if available
    return errors



######################################
# Format and Load Instructions ~ NM
######################################
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


######################################
# Demand Forecast ~ MC
######################################
def demand_forecast_parser(time):
    '''

    :param time: current time block
    :param demand_forecast: matrix with the mean times mod 288 to handle multiple days
    :return: a numpy array in the form [ Next 11 time blocks of data, sum of the 12 time blocks of data] --> len 12
    '''
    time = time % 288
    first_11_time_blocks = DEMAND_FORECAST[time:time+11]

    time = time + 11
    next_12_timeblocks = np.sum(DEMAND_FORECAST[time: time+12], axis=0)
    parsed_demand = np.vstack((first_11_time_blocks, next_12_timeblocks))

    return parsed_demand

