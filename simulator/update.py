# from simulator.state_tracker import Station, Employee, Person

from simulator.output import output
from simulator.controllers.naive.naive_controller import morning_rebalancing, evening_rebalancing

import simulator.parameters
import simulator.people

class Update:

    def __init__(self, controller, time, station_dict, customer_requests):
        self.time = time
        self.station_dict = station_dict
        self.customer_requests = customer_requests
        # self.driver_requests = driver_requests
        # self.pedestrian_requests = pedestrian_requests
        self.driver_requests = [[] for i in range(len(station_dict))]
        self.pedestrian_requests = [[] for i in range(len(station_dict))]
        self.controller = controller
        self.errors = []

    def loop(self):
        for station_index in sorted(self.station_dict):
            station = self.station_dict[station_index]

            if self.controller == "naive" or self.controller == "n":
                driver_requests, pedestrian_requests = self.naive()
            else:
                driver_requests, pedestrian_requests = self.smart()

            # Loop Arrivals
            self.arrivals(station)

            # Check for Errors
            overload = station.calc_parking() - len(station.get_en_route_list(True))

            if overload < 0:
                self.errors.append(
                    "Station {0} will have {1} more cars than it can allow".format(station, -overload))
                #self.no_park_errors[self.time][station] += 1

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



        text = output(self.time, self.station_dict)

        return text

    def arrivals(self, station):
        while len(station.en_route_list) > 0:
            person = station.en_route_list[0]
            if person.destination_time == self.time: # there is an error at time = 0
                station.en_route_list.remove(person)
                station.get_en_route_list().remove(person)
                current_vehicle_id = person.vehicle_id
                if current_vehicle_id is not None:
                    station.car_list.append(current_vehicle_id)
                if isinstance(person, self.state_tracker.Employee):
                    person.reset()
                    station.employee_list.append(person)
                else:
                    del person
            else:
                break

    def assign_drivers(self, station, driver_requests):
        for destination in driver_requests:
            driver = station.employee_list[0]
            try:
                current_car = station.car_list.pop(0)
                driver = station.employee_list.pop(0)
                driver.update_status(station.station_id, destination, self.time, current_car)
                self.station_dict[driver.destination].append_en_route_list(driver)
            except IndexError:
                self.errors.append('No car for employee at Station Number {}'.format(driver.origin))
                #self.no_car_emp_errors[self.time, driver.origin] += 1
                break

    def assign_pedestrians(self, station, pedestrian_requests):
        station_dict = self.station_dict
        for destination in pedestrian_requests:
            ped = station.employee_list.pop(0)
            ped.update_status(station.station_id, destination, self.time)
            station_dict[ped.destination].append_en_route_list(ped)

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
        #pedestrian_requests = tasks['driverRebalancingQueue']
        #vehicle_requests = tasks['vehicleRebalancingQueue']
        # idle_vehicles = []
        # idle_drivers = []
        #
        # vehicle_arrivals = np.zeros(shape=(len(station_dict), 12))
        # driver_arrivals = np.zeros(shape=(len(station_dict), 12))

        #
        # total_time_empty = np.zeros(shape=(58, 1))
        # total_time_full = np.zeros(shape=(58, 1))
        # #     ############################################
        #     # Setting Up Idle Vehicles and Drivers ~ JS
        #     ############################################
        #
        #     idle_vehicles.append(len(station_dict[station].car_list))
        #     idle_drivers.append(len(station_dict[station].employee_list))
        #
        #     ########################################
        #     # Updating Vehicle/Driver Arrivals ~ NM
        #     ########################################
        #
        #     for person in station_dict[station].get_en_route_list(True):
        #         for i in range(time, time + 12):
        #             if person.destination_time == i:
        #                 if isinstance(person, Employee):
        #                     driver_arrivals[station][i - time] += 1
        #                 if person.vehicle_id is not None:
        #                     vehicle_arrivals[station][i - time] += 1
        #             else:
        #                 break
        #
        #     ########################################
        #     # Fraction of Time for at Capacity or Empty ~ JS
        #     ########################################
        #
        #     num_parked_cars = len(station_dict[station].car_list)
        #     num_park_spots = 50 - len(station_dict[station].car_list)
        #
        #     if num_parked_cars == 0:
        #         total_time_empty[station] += 1
        #
        #     if num_parked_cars == num_park_spots:
        #         total_time_full[station] += 1
        #
        #     ######################################
        #     # Creating Forecast Dictionary ~ NM/MC
        #     ######################################
        #
        # if controller_type == 'smart':
        #     Forecast = {
        #         # 'demand' : demand_forecast_parser(time), # ~ MC
        #         'demand': demand_forecast_parser_alt(time),
        #         'vehicleArrivals': vehicle_arrivals,  # ~ NM
        #         'driverArrivals': driver_arrivals,  # ~ NM
        #     }
        #
        #     # print("FORECAST")
        #     # for k, v in Forecast.items():
        #     #     print(k, v.shape)
        #
        #     ######################################
        #     # Creating State Dictionary ~ JS
        #     ######################################
        #
        #     State = {
        #         'idleVehicles': np.array(idle_vehicles),
        #         'idleDrivers': np.array(idle_drivers),
        #         'privateVehicles': np.zeros((58, 1))
        #     }
        #
        #     # Fake data RoadNetwork
        #     # RoadNetwork = np.load("./roadNetwork.npy").item()
        #
        #     # create controller if it doesn't already exist
        #     try:
        #         controller
        #     except:
        #         controller = MoDController(RoadNetwork)
        #
        #     # Other Fake State data for testing.
        #     # Parameters = np.load("./parameters.npy").item()
        #     # State = np.load("./state.npy").item()
        #     # Forecast = np.load("./forecast.npy").item()
        #     # Flags = np.load("./flags.npy").item()
        #
        #     [tasks, controller_output] = controller.computerebalancing(Parameters, State, Forecast, Flags)
        #     # for task in tasks:
        #     #     print(task)
        #     #
        #     # for c_output in controller_output:
        #     #     print(c_output)

    def naive(self):
        morningStart, morningEnd = simulator.parameters.morningStart, simulator.parameters.morningEnd
        eveningStart, eveningEnd = simulator.parameters.eveningStart, simulator.parameters.eveningEnd
        if morningStart <= self.time and self.time <= morningEnd:
            driver_requests, pedestrian_requests = morning_rebalancing(self.station_dict)
            morningStart += 24
            morningEnd += 24
        elif eveningStart <= self.time and self.time <= eveningEnd:
            driver_requests, pedestrian_requests = evening_rebalancing(self.station_dict)
            eveningStart += 24
            eveningEnd += 24
        else:
            driver_requests, pedestrian_requests = [], []

        return driver_requests, pedestrian_requests

    def Errors(self):
        pass
    # ######################################
    # # Tracking Errors / Summing Errors ~ JS
    # ######################################
    #
    # sum_station_no_park_errors = np.sum(no_park_errors, axis=0)  # no parking errors per station total
    # sum_station_no_car_cust_errors = np.sum(no_car_cust_errors, axis=0)  # no car available for customers errors per station
    # sum_station_no_car_emp_errors = np.sum(no_car_emp_errors, axis=0)  # no car available for employees errors per station
    #
    # sum_time_no_park_errors = np.sum(no_park_errors, axis=1)  # no parking errors per time total
    # sum_time_no_car_cust_errors = np.sum(no_car_cust_errors, axis=1)  # no car available for customers errors per time total
    # sum_time_no_car_emp_errors = np.sum(no_car_emp_errors, axis=1)  # no car available for employees errors per time total

    #        self.no_car_cust_errors = np.zeros(shape=(2880, 58))
    # self.no_park_errors = np.zeros(shape=(2880, 58))
    #self.no_car_emp_errors = np.zeros(shape=(2880, 58))