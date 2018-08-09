from simulator.people import Employee, Person
from simulator.stations import Station

import numpy as np

import sys
class Update:

    def __init__(self, controller, setup_vars):

        self.station_ids = setup_vars['station_ids'].index.tolist()
        self.station_dict = self.station_initializer(setup_vars)
        self.inverted_station_map = {v: k for k, v in setup_vars['mapping'].items()}
        self.controller = controller

        self.log = {
            'parking_violation': np.zeros([58, 2880]).astype(int),
            'no_vehicle_for_customer': np.zeros([58, 2880]).astype(int),
            'no_vehicle_for_employee': np.zeros([58, 2880]).astype(int),
            'station_full': np.zeros([58, 2880]).astype(int),
            'station_empty': np.zeros([58, 2880]).astype(int),
            'available_parking': np.zeros([58, 2880]).astype(int),
            'idle_vehicles': np.zeros([58, 2880]).astype(int)
        }

        self.time = 0
        self.customer_requests = []

        self.travel_times = setup_vars['travel_time']

        if self.controller == "naive" or self.controller == "n":
            self.morning_start = 72  # 6am
            self.morning_end = 96  # 8am
            self.evening_start = 180  # 3pm
            self.evening_end = 204  # 5pm
        else:
            self.smart_controller = self.smart_setup()

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

    def loop(self, time, customer_requests):
        '''
        Loops through stations in order to handle requests
        :return:
        '''

        self.time = time
        self.customer_requests = self.convert_cust_req_to_real_stations(customer_requests)

        if self.controller == "naive" or self.controller == "n":
            driver_requests, pedestrian_requests = self.naive()
        else:
            driver_requests, pedestrian_requests = self.smart()

        for station_number in self.station_ids:

            station_obj = self.station_dict[station_number]

            driver_request = driver_requests[station_obj.station_id]
            ped_request = pedestrian_requests[station_obj.station_id]

            # Loop Arrivals
            self.arrivals(station_obj)

            # Put customers into cars
            if len(self.customer_requests) > 0:
                for customer_request in self.customer_requests:
                    if customer_request[0] == station_number:
                        self.assign_customers(station_obj, customer_request)

            # Assign Drivers
            if len(driver_request) > 0:
                for i in range(len(driver_request)):
                    request = (station_number, self.station_ids[driver_request[i]])
                    self.assign_drivers(station_obj, request)

            # Assign Pedestrians
            if len(ped_request) > 0:
                for i in range(len(ped_request)):
                    request = (station_number, self.station_ids[ped_request[i]])
                    self.assign_pedestrians(station_obj, request)

        return self.record(), self.station_dict

    def record(self):
        for station in self.station_ids:

            station = self.station_dict[station]
            logical_station = station.station_id

            # Log State and Errors
            if station.calc_parking() == 0:
                self.log['station_full'][logical_station, self.time] += 1

            if station.calc_parking() == station.parking_spots:
                self.log['station_empty'][logical_station, self.time] += 1

            self.log['idle_vehicles'][logical_station, self.time] = len(station.car_list)
            self.log['available_parking'][logical_station, self.time] = station.calc_parking()

        return self.log

    def arrivals(self, station):
        while len(station.en_route_list) > 0:

            # Grab the first person in the en_route_list
            person = station.get_en_route_list(True)[0]
            if person.destination_time == self.time:
                station.en_route_list.remove(person)

                # Check if they have a car
                if person.vehicle_id is not None:
                    if station.calc_parking() <= 0:
                        self.log['parking_violation'][station.station_id, self.time] += 1
                        self.reroute_for_overflow(person, station)
                    else:
                        station.car_list.append(person.vehicle_id)
                        # Check if they are an employee
                        if isinstance(person, Employee):
                            person.reset()
                            station.employee_list.append(person)
                        else:
                            del person
                else:
                    # We don't have to check if they are an employee because they
                    # don't have a car, so we already know
                    person.reset()
                    station.employee_list.append(person)


            else:
                break

    def assign_drivers(self, station, request):
        print('Driving {}'.format(request))

        try:
            # Try removing a car
            car = station.car_list.pop(0)

            # Update their status and remove them from the employee_list
            driver = station.employee_list.pop(0)
            driver.update_status(request[0], request[1], self.time, car)

            # Add them the en_route_list of the destination
            self.station_dict[driver.destination].en_route_list.append(driver)

        except IndexError:
            # If you can't remove a car, log the error
            print("No Car")
            self.log['no_vehicle_for_employee'][station.station_id, self.time] += 1

    def reroute_for_overflow(self, person, station):
        '''
        When a person tries to drop off a car and there is no room, this method will reroute them to the next
        closest station.
        :param person: Person who was trying to drop off a car
        :param station: Station the person was trying to drop off a car at.
        '''
        real_station_id = self.station_ids[station.station_id]

        # Get the correct travel_matrix. but drop the current station (it'll always be the closest)
        travel_matrix = self.travel_times['hamo'][real_station_id].drop(index=real_station_id)

        # Find the next closest station with available parking.
        closest_station = None
        while closest_station is None:
            closest_station = travel_matrix.idxmin()
            # Check if there's parking at the closest station, if there isn't remove that station from the matrix
            if self.station_dict[closest_station].calc_parking() == 0:
                travel_matrix = travel_matrix.drop(index=closest_station)
                closest_station = None

        print("Rerouting to station: {}, which has {} parking spots".format(closest_station, self.station_dict[
            closest_station].calc_parking()))

        # update the station the person was rerouted to
        person.update_status(real_station_id, closest_station, self.time, person.vehicle_id)
        self.station_dict[closest_station].en_route_list.append(person)

    def assign_pedestrians(self, station, request):
        print('Walking {}'.format(request))

        # Remove them from the employee list
        ped = station.employee_list.pop(0)

        # Updating their status
        ped.update_status(request[0], request[1], self.time)

        # Adding them to the en_route list of their destination
        self.station_dict[ped.destination].en_route_list.append(ped)

    def assign_customers(self, station, request):
        try:
            car = station.car_list.pop(0)

            # If there is a car, create the person object, and add them to the en_route list
            customer = Person(request[0], request[1], self.time, car)
            self.station_dict[customer.destination].en_route_list.append(customer)
        except IndexError:
            self.log['no_vehicle_for_customer'][station.station_id, self.time] += 1

    def naive(self):

        from simulator.controllers.naive.naive_controller import morning_rebalancing, evening_rebalancing

        if self.morning_start <= self.time <= self.morning_end:
            driver_requests, pedestrian_requests = morning_rebalancing(self.station_dict, self.station_ids)

            if self.time == self.morning_end:
                self.morning_start += 288
                self.morning_end += 288
        elif self.evening_start <= self.time <= self.evening_end:
            driver_requests, pedestrian_requests = evening_rebalancing(self.station_dict, self.station_ids)

            if self.time == self.evening_end:
                self.evening_start += 288
                self.evening_end += 288
        else:
            driver_requests = [[] for i in range(len(self.station_dict))]
            pedestrian_requests = [[] for i in range(len(self.station_dict))]
        return driver_requests, pedestrian_requests

    def smart(self):
        smart = self.smart_controller
        # Update the state of the Optimal Controller
        smart.update_arrivals_and_idle(self.time, self.station_dict)
        smart.update_contoller()
        smart.controller.forecast_demand(self.time)

        [tasks, output] = smart.controller.compute_rebalancing()

        return tasks['vehicleRebalancingQueue'], tasks['driverRebalancingQueue']

    def smart_setup(self):

        from simulator.controllers.smart.smart import SmartController

        smart = SmartController()
        return smart

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

