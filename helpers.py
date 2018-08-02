from classes import *
from globals import *

import numpy as np
import matlab



######################################
# Instantiating Error Arrays ~ JS
######################################

no_car_cust_errors = np.zeros(shape=(2880, 58))
no_park_errors = np.zeros(shape=(2880, 58))
no_car_emp_errors = np.zeros(shape=(2880, 58))


######################################
# Creating Functions For Update ~ NM
######################################


# def convert_real_to_logical(station):
#     return station_mapping[station]


######################################
# Update Loop ~ NM
######################################
class Update:
    def __init__(self, station_mapping, station_ids, station_dict, travel_times):
        self.station_mapping = station_mapping
        self.inverted_station_map = {v: k for k, v in station_mapping.items()}
        self.current_time = None
        self.station_ids = station_ids
        self.driver_tasks = []
        self.pedestrian_tasks = []
        self.station_dict = station_dict
        self.travel_times = travel_times

    def update_driver_ped_tasks(self, tasks, task_type):
        temp = []
        for index, task in enumerate(tasks):
            if task != matlab.double([]):
                origin = station_ids[index]
                if type(task) == float:
                    destination = station_ids[int(task)-1]
                    temp.append((origin, destination))
                else:
                    for sub_task in task[0]:  # It returns a list of one list if there are multiple tasks
                        destination = station_ids[int(sub_task)-1]
                        temp.append((origin, destination))

        if task_type == 'driver':
            self.driver_tasks = temp
            print("Driver Tasks: {}".format(self.driver_tasks))
        else:
            self.pedestrian_tasks = temp
            print("Pedestrian Tasks: {}".format(self.pedestrian_tasks))

    def convert_cust_req_to_real_stations(self, tasks):
        temp = []
        for task in tasks:
            temp.append([self.inverted_station_map[task[0]], self.inverted_station_map[task[1]]])
        return temp

    def reroute_for_overflow(self, person, station):
        '''
        When a person tries to drop off a car and there is no room, this method will reroute them to the next
        closest station.
        :param person: Person who was trying to drop off a car
        :param station: Station the person was trying to drop off a car at.
        :return:
        '''
        real_station_id = self.station_ids[station.station_id]
        # Get the correct travel_matrix. bit drop the current station (it'll always be the closest)
        if isinstance(person, Employee):
            travel_matrix = self.travel_times['hamo'].drop(index=real_station_id)
        else:
            travel_matrix = self.travel_times['car'].drop(index=real_station_id)

        closest_station = None
        while closest_station is None:
            closest_station = travel_matrix.idxmin()
            # Check if there's parking at the closest station, if there isn't remove that station from the matrix
            if self.station_dict[closest_station].available_parking == 0:
                travel_matrix = travel_matrix.drop(index=closest_station)
                closest_station = None

        station.en_route_list.remove(person)
        self.station_dict[closest_station].en_route_list.append(person)

    def update_customer_list(self, requests, time, cust_list):
        customer = Person(requests[0], requests[1], time)
        cust_list.append(customer)
        print(customer.destination_time)

    def assign_customers(self, station, station_dictionary, errors):
        while len(station.waiting_customers) > 0:
            customer = station.waiting_customers[0]
            try:
                current_car = station.car_list.pop(0)
                customer = station.waiting_customers.pop(0)
                customer.assign_cust_car(current_car)
                station_dictionary[customer.destination].append_en_route_list(customer)
                print("Customer put in car")
            except IndexError:
                errors.append('No car for customer at Station Number {}'.format(customer.origin))
                print("No car for customer")
                # no_car_cust_errors[current_time, customer.origin] += 1
                no_car_cust_errors[self.current_time, station.station_id] += 1  # ADDED
                break
            print("length of customer_list: {}".format(len(station.waiting_customers)))

    def assign_pedestrians(self):
        for task in self.pedestrian_tasks:
            ped = self.station_dict[task[0]].employee_list.pop(0)
            ped.update_status(task[0], task[1], self.current_time)
            self.station_dict[task[1]].append_en_route_list(ped)

    def assign_drivers(self, errors):

        for task in self.driver_tasks:
            origin_station = self.station_dict[task[0]]
            driver = origin_station.employee_list[0]
            try:
                current_car = origin_station.car_list.pop(0)
                driver = origin_station.employee_list.pop(0)
                driver.update_status(task[0], task[1], self.current_time, current_car)
                self.station_dict[task[1]].append_en_route_list(driver)
            except IndexError:
                errors.append('No car for employee at Station Number {}'.format(driver.origin))
                no_car_emp_errors[self.current_time, station.station_id] += 1
                break

    def update_employee_list(self, requests, employee_list):
        for employee in requests:
            emp_id = employee_list[employee]
            employee_list[employee] = Employee(requests[0], requests[1], self.current_time, emp_id)

    def arrivals(self, station):
        while len(station.en_route_list) > 0:
            person = station.get_en_route_list(True)[0]
            if person.destination_time == self.current_time:
                station.get_en_route_list().remove(person)
                current_vehicle_id = person.vehicle_id
                if current_vehicle_id is not None:
                    if station.available_parking > 0:
                        station.car_list.append(current_vehicle_id)
                        if isinstance(person, Employee):
                            person.reset()
                            station.employee_list.append(person)
                        else:
                            del person
                    else:
                        print("no parking")  #TODO log me
                        self.reroute_for_overflow(person, station)
                else:
                    person.reset()
                    station.employee_list.append(person)

            else:
                break

    def run(self, station_dict, customer_requests, current_time, stations, driver_requests=[], pedestrian_requests=[]):
        self.current_time = current_time
        errors = []

        # if we're using real station numbers this converts the cust requests into "real" format
        customer_requests = self.convert_cust_req_to_real_stations(customer_requests)

        for logical_station, station in enumerate(self.station_ids):  # Goes through the stations in order
            # For future efficiency check to see if there are any requests before doing all this work
            # Grab information relevant to this loop and organize
            current_station = station_dict[station]

            # Loop Arrivals - Need to check
            self.arrivals(current_station)



            # Put customers into cars
            if len(customer_requests) > 0:
                # Update Customer list and Assign Them
                for customer_request in customer_requests:
                    if customer_request[0] == station:
                        self.update_customer_list(customer_request,
                                                  current_time,
                                                  current_station.waiting_customers)

                        print("CUSTOMER REQUEST: {}".format(customer_request))
                        print("Station: {}, Car Count: {}".format(station, len(current_station.car_list)))

                # assigns customers to cars if available
                self.assign_customers(current_station, station_dict, errors)



        # Send out drivers and pedestrians on tasks

        self.assign_drivers(errors)
        self.assign_pedestrians()

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


# def demand_forecast_parser(time):
#     """
#     :param time: current time block
#     :param demand_forecast: matrix with the mean times mod 288 to handle multiple days
#     :return: a numpy array in the form [ Next 11 time blocks of data, sum of the 12 time blocks of data] --> len 12
#     """
#     time = time % 288
#     first_11_time_blocks = DEMAND_FORECAST[time:time + 11]
#
#     time = time + 11
#     next_12_time_blocks = np.sum(DEMAND_FORECAST[time: time + 12], axis=0)
#     parsed_demand = np.vstack((first_11_time_blocks, next_12_time_blocks))
#
#     return parsed_demand
#
#
# def demand_forecast_parser_alt(time):
#     time = time % 288  # For dealing with multiple days
#     first_11_time_blocks = DEMAND_FORECAST_ALT[:, :, time:time + 11]
#     time += 11
#     next_12_time_blocks = np.sum(DEMAND_FORECAST_ALT[:, :, time: time + 12], axis=2)
#     parsed_demand = np.zeros((first_11_time_blocks.shape[0],
#                               first_11_time_blocks.shape[1],
#                               first_11_time_blocks.shape[2] + 1))
#
#     for station in range(first_11_time_blocks.shape[0]):
#         parsed_demand[station] = np.hstack((first_11_time_blocks[station], next_12_time_blocks[station].reshape((58, 1))))
#
#     return parsed_demand






def morning_rebalancing(dict):
    driver_task = [[] for i in range(58)]
    pedestrian_task = [[] for i in range(58)]
    home = (22, 55)
    buffer = (38, 41)
    extra = (37,43)
    for i in home:
        station = dict[i]
        for emp in station.employee_list:
            if len(station.car_list) > 0:
                for dest in buffer:
                    if dict[dest].available_parking > 0:
                        driver_task[i] = dest
                        break
                else:
                    for dest in extra:
                        if dict[dest].parking_spots > 0:
                            driver_task[i] = dest
                    else:
                        break

    for i in buffer + extra:
        if dict[home[0]].available_parking + dict[home[1]] == 0:
            break
        station = dict[i]
        if dict[home[0]].available_parking > dict(home[1]).available_parking:
            dest = dict[home[1]]
        else:
            dest = dict[home[0]]

        for emp in station.employee_list:
            pedestrian_task[i] = dest

    return driver_task, pedestrian_task

def evening_rebalancing(dict):
    driver_task = [[] for i in range(58)]
    pedestrian_task = [[] for i in range(58)]
    home = (22, 55)
    buffer = (38, 41)
    extra = (37, 43)
    for i in buffer+extra:
        station = dict[i]
        for emp in station.employee_list:
            if len(station.car_list) > 0:
                for dest in buffer:
                    if dict[dest].available_parking > 0:
                        driver_task[i] = dest
                        break
                else:
                    for dest in extra:
                        if dict[dest].parking_spots > 0:
                            driver_task[i] = dest
                    else:
                        break
            else:
                break

    for i in home:
        station = dict[i]
        if dict(home[0]).available_parking > dict(home[1]).available_parking:
            dest = dict[home[1]]
        else:
            dest = dict[home[0]]

        for emp in station.employee_list:
            pedestrian_task[i] = dest



    return driver_task, pedestrian_task