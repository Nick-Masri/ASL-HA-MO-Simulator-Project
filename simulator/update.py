# from simulator.state_tracker import Station, Employee, Person

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
        # self.driver_requests = driver_requests
        # self.pedestrian_requests = pedestrian_requests
        self.driver_requests = [[] for i in range(len(station_dict))]
        self.pedestrian_requests = [[] for i in range(len(station_dict))]
        self.controller = controller
        self.errors = []
        self.tool = tool

    def loop(self):
        for station_index in sorted(self.station_dict):
            station = self.station_dict[station_index]

            if self.controller == "naive" or self.controller == "n":
                driver_requests, pedestrian_requests = self.naive()
            else:
                driver_requests, pedestrian_requests = self.smart()

            # Loop Arrivals
            self.arrivals(station)
            self.tool.measure(self.time, station, station_index)

            # Put customers into cars
            if len(self.customer_requests) > 0:
                # Update Customer list and Assign Them
                for customer_request in self.customer_requests:
                    if customer_request[0] == station:
                        # add to station cust waiting list
                        self.update_customer_list(station, customer_request)

                        print("CUSTOMER REQUEST: {}".format(customer_request))

                # assigns customers to cars if available
                self.assign_customers(station)

            if len(self.driver_requests[station_index]) > 0 or len(self.pedestrian_requests[station_index]) > 0:

                # Assign drivers
                self.assign_drivers(station, driver_requests)

                # Assign Pedestrians
                self.assign_pedestrians(station, pedestrian_requests)

            # print(pedestrian_requests)
            # print(driver_requests)
            for origin, pedestrian_request in enumerate(pedestrian_requests):
                if pedestrian_request != []:
                    if origin == station_index:
                        request = (origin, pedestrian_request[0], self.time)
                        self.assign_pedestrians(request, station, self.station_dict)

            for origin, driver_request in enumerate(driver_requests):
                if driver_request != []:
                    if origin == station_index:
                        request = (origin, driver_request[0], self.time)
                        self.assign_drivers(request, station, self.station_dict, self.errors)

        text = output(self.time, self.station_dict)

        return text

    def arrivals(self, station):
        while len(station.en_route_list) > 0:
            person = station.get_en_route_list(True)[0]
            if person.destination_time == self.time:
                station.get_en_route_list().remove(person)
                current_vehicle_id = person.vehicle_id
                if current_vehicle_id is not None:
                    station.car_list.append(current_vehicle_id)
                if isinstance(person, Employee):
                    person.reset()
                    station.employee_list.append(person)
                else:
                    del person
            else:
                break

    def assign_drivers(self, request, station, station_dictionary, errors):
        print('Driving {}'.format(request))
        driver = station.employee_list[0]
        try:
            driver = station.employee_list.pop(0)
            driver = simulator.people.Employee(request[0], request[1], request[2])
            current_car = station.car_list.pop(0)
            driver.update_status(driver, current_car)
            station_dictionary[driver.destination].append_en_route_list(driver)
        except IndexError:
            errors.append('No car for employee at Station Number {}'.format(driver.origin))

    def assign_pedestrians(self, request, station, station_dictionary):
        print('Walking {}'.format(request))
        ped = station.employee_list.pop(0)
        ped = simulator.people.Employee(request[0], request[1], request[2])
        station_dictionary[ped.destination].append_en_route_list(ped)

    def update_customer_list(self, station, request):
        customer = self.state_tracker.Person(request[0], request[1], self.time)
        station.customer_list.append(customer)

    def assign_customers(self, station):
        while len(station.waiting_customers) > 0:
            customer = station.waiting_customers[0]
            try:
                current_car = station.car_list.pop(0)
                customer = station.waiting_customers.pop(0)
                customer.assign_car(current_car)
                self.station_dict[customer.destination].append_en_route_list(customer)
            except IndexError:
                self.errors.append('No car for customer at Station Number {}'.format(customer.origin))
                #self.no_car_cust_errors[self.time, customer.origin] += 1
                break

    def smart(self):
        return [], []
        pedestrian_requests = tasks['driverRebalancingQueue']
        vehicle_requests = tasks['vehicleRebalancingQueue']
        idle_vehicles = []
        idle_drivers = []

        vehicle_arrivals = np.zeros(shape=(len(station_dict), 12))
        driver_arrivals = np.zeros(shape=(len(station_dict), 12))

        idle_vehicles.append(len(station_dict[station].car_list))
        idle_drivers.append(len(station_dict[station].employee_list))


        for person in station_dict[station].get_en_route_list(True):
            for i in range(time, time + 12):
                if person.destination_time == i:
                    if isinstance(person, Employee):
                        driver_arrivals[station][i - time] += 1
                    if person.vehicle_id is not None:
                        vehicle_arrivals[station][i - time] += 1

        Forecast = {
            'demand': demand_forecast_parser_alt(time),
            'vehicleArrivals': vehicle_arrivals,  # ~ NM
            'driverArrivals': driver_arrivals,  # ~ NM
        }

        State = {
            'idleVehicles': np.array(idle_vehicles),
            'idleDrivers': np.array(idle_drivers),
            'privateVehicles': np.zeros((58, 1))
        }

        try:
            controller
        except:
            controller = MoDController(RoadNetwork)

        [tasks, controller_output] = controller.computerebalancing(Parameters, State, Forecast, Flags)
        return tasks, controller
    def naive(self):
        morningStart = simulator.parameters.morningStart
        morningEnd = simulator.parameters.morningEnd
        eveningStart = simulator.parameters.eveningStart
        eveningEnd = simulator.parameters.eveningEnd

        if morningStart <= self.time and self.time <= morningEnd:
            driver_requests, pedestrian_requests = morning_rebalancing(self.station_dict)
            if self.time == morningEnd:
                simulator.parameters.morningStart += 288
                simulator.parameters.morningEnd += 288
        elif eveningStart <= self.time and self.time <= eveningEnd:
            driver_requests, pedestrian_requests = evening_rebalancing(self.station_dict)
            if self.time == eveningEnd:
                simulator.parameters.eveningStart += 288
                simulator.parameters.eveningEnd += 288
        else:
            driver_requests, pedestrian_requests = [], []

        return driver_requests, pedestrian_requests
