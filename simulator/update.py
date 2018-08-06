from simulator.output import overview

from simulator.controllers.naive.naive_controller import morning_rebalancing, evening_rebalancing
from simulator.controllers.smart.smart import SmartController

import simulator.variables.parameters
from simulator.people import Employee, Person

import numpy as np
import math

from simulator.variables.formatting import hamo_travel_times


#########################
# Update Function ~ NM
#########################


class Update:

    def __init__(self, tool, controller, time, station_dict, customer_requests):
        self.time = time
        self.station_dict = station_dict
        self.customer_requests = customer_requests
        self.controller = controller
        self.errors = []
        self.no_parking = 0
        self.no_idle_vehicle = 0
        self.tool = tool
        self.idle_vehicles = np.zeros([58,])
        self.available_parking = np.zeros([58,])

    def loop(self):
        for station_index in sorted(self.station_dict):

            if self.controller == "naive" or self.controller == "n":
                driver_requests, pedestrian_requests = self.naive()
            else:
                driver_requests = [[] for i in range(len(self.station_dict))]
                pedestrian_requests = [[] for i in range(len(self.station_dict))]

            station = self.station_dict[station_index]
            driver_request = driver_requests[station_index]
            ped_request = pedestrian_requests[station_index]

            # Loop Arrivals
            self.arrivals(station, station_index)
            self.tool.measure_station(self.time, station, station_index)

            # Put customers into cars
            if len(self.customer_requests) > 0:
                for customer_request in self.customer_requests:
                    if customer_request[0] == station_index:
                        self.assign_customers(station, customer_request, station_index)

            if len(driver_request) > 0:
                request = (station_index, driver_request[0], self.time)
                self.assign_drivers(station, request, station_index)

            if len(ped_request) > 0:
                request = (station_index, ped_request[0], self.time)
                self.assign_pedestrians(station, request)

            self.idle_vehicles[station_index] = len(station.car_list)
            self.available_parking[station_index] = station.calc_parking()

        # self.tool.park_errors += self.no_parking
        # self.tool.vehicle_errors += self.no_idle_vehicle

        # self.tool.vehicle_errors[station_index, math.floor(self.time / 288)]
        text = overview(self.time, self.station_dict)
        return text, self.idle_vehicles, self.available_parking

    def arrivals(self, station, station_index):
        while len(station.en_route_list) > 0:
            person = station.get_en_route_list(True)[0]
            if person.destination_time == self.time:
                station.en_route_list.remove(person)
                if person.vehicle_id is not None:
                    if station.calc_parking() <= 0:
                        if station.parking_spots != 0:
                            # self.no_parking += 1
                            self.tool.park_errors[station_index, math.floor(self.time / 288)] += 1
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

    def assign_drivers(self, station, request, station_index):
        print('Driving {}'.format(request))
        station.employee_list.pop(0)
        driver = Employee(request[0], request[1], request[2])
        try:
            driver.vehicle_id = station.car_list.pop(0)
            self.station_dict[driver.destination].en_route_list.append(driver)
        except IndexError:
            if station.parking_spots != 0:
                self.tool.vehicle_errors[station_index, math.floor(self.time / 288)] += 1
                print("No Parking at time: {0}, at station: {1}".format(self.time, driver.destination))

    def reroute_for_overflow(self, person):
        '''
        When a person tries to drop off a car and there is no room, this method will reroute them to the next
        closest station.
        :param person: Person who was trying to drop off a car
        :param station: Station the person was trying to drop off a car at.
        :return:
        '''
        travel_matrix = hamo_travel_times[person.destination].copy()
        travel_matrix[person.destination] = 1000 # Set the travel time of the current station to 1000

        # Find the next closest station with available parking.
        closest_station = None
        while closest_station is None:
            # closest_station = travel_matrix.idxmin()

            closest_station = np.argmin(travel_matrix)
            # Check if there's parking at the closest station, if there isn't remove that station from the matrix
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

    def assign_customers(self, station, request, station_index):
        if station.parking_spots != 0:
            customer = Person(request[0], request[1], self.time)
            try:
                current_car = station.car_list.pop(0)
                customer.vehicle_id = current_car
                self.station_dict[customer.destination].en_route_list.append(customer)
            except IndexError:
                if station.parking_spots != 0:
                    self.no_idle_vehicle += 1
                    self.tool.vehicle_errors[station_index, math.floor(self.time / 288)] += 1
                    print("No Idle Vehicle at time: {0}, at station: {1}, heading to station {2}".format(self.time, customer.origin, customer.destination))

    def naive(self):

        morning_start = simulator.variables.parameters.morningStart
        morning_end = simulator.variables.parameters.morningEnd
        evening_start = simulator.variables.parameters.eveningStart
        evening_end = simulator.variables.parameters.eveningEnd

        if morning_start <= self.time <= morning_end:
            driver_requests, pedestrian_requests = morning_rebalancing(self.station_dict)

            if self.time == morning_end:
                simulator.variables.parameters.morningStart += 288
                simulator.variables.parameters.morningEnd += 288
        elif evening_start <= self.time <= evening_end:
            driver_requests, pedestrian_requests = evening_rebalancing(self.station_dict)

            if self.time == evening_end:
                simulator.variables.parameters.eveningStart += 288
                simulator.variables.parameters.eveningEnd += 288
        else:
            driver_requests = [[] for i in range(len(self.station_dict))]
            pedestrian_requests = [[] for i in range(len(self.station_dict))]
        return driver_requests, pedestrian_requests

    def smart(self):
        smart = SmartController()
        smart.initialize()