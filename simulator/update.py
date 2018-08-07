from simulator.output.overview import output

from simulator.people import Employee, Person
from simulator.stations import Station

import numpy as np

import math

import sys

#########################
# Update Function ~ NM
#########################


class Update:

    def __init__(self, tool, controller, time, customer_requests, travel_times, setup_vars):
        self.time = time

        self.station_ids = setup_vars['station_ids'].index.tolist()

        self.station_dict = self.station_initializer(setup_vars)

        self.inverted_station_map = {v: k for k, v in setup_vars['mapping'].items()}
        self.controller = controller

        self.customer_requests = self.convert_cust_req_to_real_stations(customer_requests)
        self.tool = tool
        self.errors = {
            'parking_violation': [],
            'no_vehicle_for_customer': [],
            'no_vehicle_for_employee': [],
            'station_full': [],
            'station_empty': [],
            'available_parking': [],
            'idle_vehicles': []
        }
        # self.idle_vehicles = np.zeros([58,])
        # self.available_parking = np.zeros([58,])
        self.travel_times = travel_times

    def convert_cust_req_to_real_stations(self, tasks):
        '''
        Converts the station Requests to the 'real_ids'. The customer requests from 'hamo10days.npy' use the staton
        map (or in this case the 'inverted_station_map' to convert to "real station ids".
        :param tasks: List of (o, d) format, where o and d are the logical values found in 'inverted_station_map'
        '''
        temp = []
        for task in tasks:
            temp.append([self.inverted_station_map[task[0]], self.inverted_station_map[task[1]]])
        return temp

    def loop(self):
        for station in self.station_ids:

            station = self.station_dict[station]

            if self.controller == "naive" or self.controller == "n":
                driver_requests, pedestrian_requests = self.naive()
            else:
                driver_requests = [[] for i in range(len(self.station_dict))]
                pedestrian_requests = [[] for i in range(len(self.station_dict))]

            logical_station = station.station_id

            driver_request = driver_requests[logical_station]
            ped_request = pedestrian_requests[logical_station]

            # Loop Arrivals
            self.arrivals(station)
            self.tool.measure_station(self.time, station)

            # Put customers into cars
            if len(self.customer_requests) > 0:
                for customer_request in self.customer_requests:
                    if customer_request[0] == logical_station:
                        self.assign_customers(station, customer_request)

            if len(driver_request) > 0:
                request = (logical_station, driver_request[0], self.time)
                self.assign_drivers(station, request)

            if len(ped_request) > 0:
                request = (logical_station, ped_request[0], self.time)
                self.assign_pedestrians(station, request)

            # self.idle_vehicles[station_index] = len(station.car_list)
            # self.available_parking[station_index] = station.calc_parking()

        # self.tool.park_errors += self.no_parking
        # self.tool.vehicle_errors += self.no_idle_vehicle

        # self.tool.vehicle_errors[station_index, math.floor(self.time / 288)]
        text = output(self.time, self.station_dict)
        return text, self.errors

    def arrivals(self, station):
        while len(station.en_route_list) > 0:
            person = station.get_en_route_list(True)[0]
            if person.destination_time == self.time:
                station.en_route_list.remove(person)
                if person.vehicle_id is not None:
                    if station.calc_parking() <= 0:
                        if station.parking_spots != 0:
                            # self.no_parking += 1
                            pass
                            # self.tool.park_errors[station., math.floor(self.time / 288)] += 1
                        self.reroute_for_overflow(person)
                    else:
                        station.car_list.append(person.vehicle_id)
                        if isinstance(person, Employee):
                            person.reset()
                            station.employee_list.append(person)
                        else:
                            del person

                else:
                    person.reset()
                    station.employee_list.append(person)

            else:
                break

    def assign_drivers(self, station, request):
        print('Driving {}'.format(request))
        station.employee_list.pop(0)
        driver = Employee(request[0], request[1], request[2])
        try:
            driver.vehicle_id = station.car_list.pop(0)
            self.station_dict[driver.destination].en_route_list.append(driver)
        except IndexError:
            if station.parking_spots != 0:
                # self.tool.vehicle_errors[station_index, math.floor(self.time / 288)] += 1
                # print("No Parking at time: {0}, at station: {1}".format(self.time, driver.destination))
                pass
    def reroute_for_overflow(self, person):
        '''
        When a person tries to drop off a car and there is no room, this method will reroute them to the next
        closest station.
        :param person: Person who was trying to drop off a car
        :param station: Station the person was trying to drop off a car at.
        :return:
        '''
        travel_matrix = self.travel_times['hamo'][person.destination].copy()
        travel_matrix[person.destination] = 1000 # Set the travel time of the current station to 1000

        # Find the next closest station with available parking_per_station.
        closest_station = None
        while closest_station is None:
            # closest_station = travel_matrix.idxmin()

            closest_station = np.argmin(travel_matrix)
            # Check if there's parking_per_station at the closest station, if there isn't remove that station from the matrix
            if self.station_dict[closest_station].calc_parking() == 0:
                # closest_station not in (11, 37, 27, 10, 2, 5):
                travel_matrix[closest_station] = 1000
                # travel_matrix = travel_matrix.drop(index=closest_station)
                closest_station = None
        # for x in (11, 37, 27, 10, 2, 5):
        #     closest_
        # update the station the person was rerouted to
        self.station_dict[closest_station].en_route_list.append(person)
        person.update_status((person.destination, closest_station, self.time), person.vehicle_id)

    def assign_pedestrians(self, station, request):
        print('Walking {}'.format(request))
        station.employee_list.pop(0)
        ped = Employee(request[0], request[1], request[2])
        self.station_dict[ped.destination].en_route_list.append(ped)

    def assign_customers(self, station, request):
        if station.parking_spots != 0:
            customer = Person(request[0], request[1], self.time)
            try:
                current_car = station.car_list.pop(0)
                customer.vehicle_id = current_car
                self.station_dict[customer.destination].en_route_list.append(customer)
            except IndexError:
                if station.parking_spots != 0:
                    # self.no_idle_vehicle += 1
                    # self.tool.vehicle_errors[station_index, math.floor(self.time / 288)] += 1
                    # print("No Idle Vehicle at time: {0}, at station: {1}, heading to station {2}".format(self.time, customer.origin, customer.destination))
                    pass
    def naive(self):

        from simulator.controllers.naive.naive_controller import morning_rebalancing, evening_rebalancing

        morning_start = 72  # 6am
        morning_end = 96  # 8am

        evening_start = 180  # 3pm
        evening_end = 204  # 5pm

        if morning_start <= self.time <= morning_end:
            driver_requests, pedestrian_requests = morning_rebalancing(self.station_dict)

            if self.time == morning_end:
                morning_start += 288
                morning_end += 288
        elif evening_start <= self.time <= evening_end:
            driver_requests, pedestrian_requests = evening_rebalancing(self.station_dict)

            if self.time == evening_end:
                evening_start += 288
                evening_end += 288
        else:
            driver_requests = [[] for i in range(len(self.station_dict))]
            pedestrian_requests = [[] for i in range(len(self.station_dict))]
        return driver_requests, pedestrian_requests

    def smart(self):
        pass

    def smart_setup(self):

        from simulator.controllers.smart.smart import SmartController

        smart = SmartController()
        smart.initialize()

    def station_initializer(self, setup_vars):
        parking = setup_vars['parking']
        employees_at_stations = setup_vars['employees']
        cars_per_station = setup_vars['cars']

        station_dict = {}
        car_count = 1
        for logical_station, station in enumerate(self.station_ids):
            parking_spots = parking[station]
            # Assign cars to the station.
            car_list = []
            for car in range(cars_per_station[station]):
                car_list.append(car_count)
                car_count += 1

            emp_list = []
            if station in employees_at_stations.keys():
                for emp in range(employees_at_stations[station]):
                    emp_list.append(Employee(None, None, None))
            # Create the station
            station_dict[station] = Station(logical_station, parking_spots, car_list, emp_list)

        return station_dict

