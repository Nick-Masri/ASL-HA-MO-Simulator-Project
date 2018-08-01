from simulator.output import output
from simulator.measurement import Measurement
from simulator.controllers.naive.naive_controller import morning_rebalancing, evening_rebalancing

import simulator.parameters
from simulator.people import Employee, Person

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
        self.tool = tool

    def loop(self):
        for station_index in sorted(self.station_dict):
            station = self.station_dict[station_index]

            if self.controller == "naive" or self.controller == "n":
                driver_requests, pedestrian_requests = self.naive()
            else:
                driver_requests, pedestrian_requests = [], []

            # Loop Arrivals
            self.arrivals(station)
            self.tool.measure(self.time, station, station_index)

            # Put customers into cars
            if len(self.customer_requests) > 0:
                for customer_request in self.customer_requests:
                    if customer_request[0] == station_index:
                        self.assign_customers(station, customer_request)

            if len(driver_requests[station_index]) > 0:
                request = 
                self.assign_drivers(station, driver_requests[station_index])
            if len(pedestrian_requests[station_index]) > 0:
                self.assign_pedestrians(station, pedestrian_requests)



            # for origin, pedestrian_request in enumerate(pedestrian_requests):
            #     if pedestrian_request:
            #         if origin == station_index:
            #             request = (origin, pedestrian_request[0], self.time)
            #             self.assign_pedestrians(request, station)
            #
            # for origin, driver_request in enumerate(driver_requests):
            #     if driver_request:
            #         if origin == station_index:
            #             request = (origin, driver_request[0], self.time)
            #             self.assign_drivers(request, station)

        text = output(self.time, self.station_dict)

        return text

    def arrivals(self, station):
        while len(station.en_route_list) > 0:
            person = station.get_en_route_list(True)[0]
            if person.destination_time == self.time:
                station.en_route_list.remove(person)
                if person.vehicle_id is not None:
                    station.car_list.append(person.vehicle_id)
                    if station.calc_parking() < 0:
                        self.errors.append("No parking for person arriving at time {}".format(self.time))
                        print("No parking")
                if isinstance(person, Employee):
                    person.reset()
                    station.employee_list.append(person)
                else:
                    del person
            else:
                break

    def assign_drivers(self, station, requests):
        # print('Driving {}'.format(request))

        driver = station.employee_list[0]
        try:
            station.employee_list.remove(0)
            driver = Employee(request[0], request[1], request[2])
            driver.update_status(driver, station.car_list.pop(0))
            self.station_dict[driver.destination].en_route_list.append(driver)
        except IndexError:
            self.errors.append('No car for employee at Station Number {}'.format(driver.origin))

    def assign_pedestrians(self, request, station):
        # print('Walking {}'.format(request))
        station.employee_list.remove(0)
        ped = Employee(request[0], request[1], request[2])
        self.station_dict[ped.destination].en_route_list.append(ped)

    def assign_customers(self, station, request):
        customer = Person(request[0], request[1], self.time)
        try:
            current_car = station.car_list.pop(0)
            customer.vehicle_id = current_car
            self.station_dict[customer.destination].en_route_list.append(customer)
        except IndexError:
            self.errors.append('No car for customer at Station Number {}'.format(customer.origin))

    def naive(self):

        morning_start = simulator.parameters.morningStart
        morning_end = simulator.parameters.morningEnd
        evening_start = simulator.parameters.eveningStart
        evening_end = simulator.parameters.eveningEnd

        if morning_start <= self.time <= morning_end:
            driver_requests, pedestrian_requests = morning_rebalancing(self.station_dict)

            if self.time == morning_end:
                simulator.parameters.morningStart += 288
                simulator.parameters.morningEnd += 288
        elif evening_start <= self.time <= evening_end:
            driver_requests, pedestrian_requests = evening_rebalancing(self.station_dict)

            if self.time == evening_end:
                simulator.parameters.eveningStart += 288
                simulator.parameters.eveningEnd += 288
        else:
            driver_requests = [[] for i in range(len(self.station_dict))]
            pedestrian_requests = [[] for i in range(len(self.station_dict))]
        return driver_requests, pedestrian_requests
