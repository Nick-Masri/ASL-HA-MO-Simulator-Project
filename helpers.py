from classes import *
from globals import *

######################################
# Instantiating Error Arrays ~ JS
######################################

noCarCustErrors = np.zeros(shape=(2880, 58))
noParkErrors = np.zeros(shape=(2880, 58))
noCarEmpErrors = np.zeros(shape=(2880, 58))

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

def update_employee_list(requests, time, employee_list):
    for employee in requests:
        id = employee_list[employee]
        employee_list[employee] = Employee(requests[0], requests[1], time, id)

def assign_drivers(station, driver_tasks, station_dictionary, errors, current_time):
    for destination in driver_tasks:

        driver = station.employee_list[0]
        try:
            current_car = station.car_list.pop(0)
            driver = station.employee_list.pop(0)
            driver.update_status(station.station_id, destination, current_time, current_car)
            station_dictionary[driver.destination].append_en_route_list(driver)
        except IndexError:
            errors.append('No car for employee at Station Number {}'.format(driver.origin))
            noCarEmpErrors[current_time, driver.origin] += 1
            break


def assign_pedestrians(station, pedestrian_tasks, station_dictionary, current_time):
    for destination in pedestrian_tasks:
        ped = station.employee_list.pop(0)
        ped.update_status(station.station_id, destination, current_time)
        station_dictionary[ped.destination].append_en_route_list(ped)




def update_customer_list(requests, time, cust_list):
    customer = Person(requests[0], requests[1], time)
    cust_list.append(customer)



def assign_customers(customer_list, cars, station_dictionary, errors, current_time):
    while len(customer_list) > 0:
        customer = customer_list[0]
        try:
            current_car = cars.pop(0)
            customer = customer_list.pop(0)
            customer.assign_cust_car(current_car)
            station_dictionary[customer.destination].append_en_route_list(customer)
        except IndexError:
            errors.append('No car for customer at Station Number {}'.format(customer.origin))
            noCarCustErrors[current_time, customer.origin] += 1
            break



######################################
# Update Loop ~ NM
######################################

def update(station_dict, customer_requests, current_time, driver_requests=[], pedestrian_requests=[]):
    errors = []
    for station in sorted(station_dict):  # now it goes through the stations in order

        # For future efficiency check to see if there are any requests before doing all this work.

        # Grab information relevant to this loop and organize
        current_station = station_dict[station]
        current_car_list = current_station.car_list
        employee_list = current_station.employee_list
        customer_list = current_station.get_waiting_customers(True)
        en_route_list = current_station.get_en_route_list(True)

        # Loop Arrivals
        arrivals(en_route_list, current_time, current_car_list, employee_list, current_station)

        # Check for Errors ******** Is this assuming the capacity is 50 for each station? ***********
        overload = 50 - (len(current_station.car_list) + len(current_station.get_en_route_list()))

        if overload < 0:
            errors.append("Station {0}  will have {1} more cars than it can allow".format(current_station, -overload))
            noParkErrors[current_time, current_station] += 1

        # Put customers into cars
        if len(customer_requests) > 0:
            # Update Customer list and Assign Them
            for customer_request in customer_requests:
                if customer_request[0] == station:
                    update_customer_list(customer_request, current_time, customer_list)  # add to station cust waiting list
                    print("CUST REQUEST: {}".format(customer_request))
            assign_customers(customer_list, current_car_list, station_dict, errors, current_time)  # assigns customers to cars if available

        if len(driver_requests[station]) > 0 or len(pedestrian_requests[station]) > 0:
            print('*****************************')
            print('# of Driver Tasks: {}'.format(len(driver_requests[station])))
            print('# of Ped Tasks: {}'.format(len(pedestrian_requests[station])))
            print('*****************************')
            # Assign drivers
            assign_drivers(current_station, driver_requests[station], station_dict, errors, current_time)  # Update employee object and add it to destination enroute list
            # Assign Pedestrians
            assign_pedestrians(current_station, pedestrian_requests[station], station_dict, current_time)  # Update employee object and add it to destination enroute list (no car and time travel)


    return errors



######################################
# Format and Load Instructions ~ NM / MC
######################################
def format_instructions(request):
    var = []
    count = 0
    for req in request:
        request_indices = np.nonzero(req)
        temp = []
        num_of_requests = len(request_indices[0])  # Number of (o, d) NOT the number of requests per (o, d)
        if num_of_requests > 0:
            for request in range(num_of_requests):
                origin = request_indices[0][request]
                destination = request_indices[1][request]
                for num in range(int(req[origin][destination])):  # Loop for number of custs going from (o, d)
                    temp.append((origin, destination))
                    count += 1
        var.append(temp)
    return var

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
    first_11_timeblocks = DEMAND_FORECAST[time:time+11]

    time = time + 11
    next_12_timeblocks = np.sum(DEMAND_FORECAST[time: time+12], axis=0)
    parsed_demand = np.vstack((first_11_timeblocks, next_12_timeblocks))

    return parsed_demand


def demand_forecast_parser_alt(time):
    time = time % 288  # For dealing with multiple days
    first_11_timeblocks = DEMAND_FORECAST_ALT[:, :, time:time+11]
    time += 11
    next_12_timeblocks = np.sum(DEMAND_FORECAST_ALT[:, :, time: time+12], axis=2)
    parsed_demand = np.zeros((first_11_timeblocks.shape[0],
                              first_11_timeblocks.shape[1],
                              first_11_timeblocks.shape[2]+1))

    for station in range(first_11_timeblocks.shape[0]):
        parsed_demand[station] = np.hstack((first_11_timeblocks[station], next_12_timeblocks[station].reshape((58,1))))

    return parsed_demand

