import state_tracker

class Update:

    def __init__(self, current_time, station_dict, customer_requests, driver_requests, pedestrian_requests):
        self.current_time = current_time
        self.station_dict = station_dict
        self.customer_requests = customer_requests
        self.driver_requests = driver_requests
        self.pedestrian_requests = pedestrian_requests

        self.errors = []
        self.no_car_cust_errors = np.zeros(shape=(2880, 58))
        self.no_park_errors = np.zeros(shape=(2880, 58))
        self.no_car_emp_errors = np.zeros(shape=(2880, 58))

    def loop(self):
        for station in sorted(self.station_dict):
            self.station = self.station_dict[station]
            self.employee_list = station.employee_list
            self.car_list = station.car_list
            self.customer_list = station.get_waiting_customers(True)
            self.en_route_list = station.get_en_route_list(True)

            # Loop Arrivals
            self.arrivals(self.en_route_list, self.current_time, self.car_list, self.employee_list, self.station)

            # Check for Errors ******** This is assuming the capacity is 50 for each station ***********
            overload = station.available_parking - (len(current_station.car_list) + len(current_station.get_en_route_list()))

            if overload < 0:
                self.errors.append(
                    "Station {0} will have {1} more cars than it can allow".format(current_station, -overload))
                self.no_park_errors[current_time][current_station] += 1

            # Put customers into cars
            if len(customer_requests) > 0:
                # Update Customer list and Assign Them
                for customer_request in customer_requests:
                    if customer_request[0] == station:
                        # add to station cust waiting list
                        self.update_customer_list(customer_request, current_time, customer_list)

                        print("CUSTOMER REQUEST: {}".format(customer_request))

                # assigns customers to cars if available
                self.assign_customers(customer_list, current_car_list, station_dict, errors, current_time)

            if len(driver_requests[station]) > 0 or len(pedestrian_requests[station]) > 0:


                # Assign drivers
                self.assign_drivers(current_station, driver_requests[station], station_dict, errors, current_time)

                # Assign Pedestrians
                self.assign_pedestrians(current_station, pedestrian_requests[station], station_dict, current_time)

        return errors

    def arrivals(self):
        while len(self.en_route_list) > 0:
            person = self.en_route_list[0]
            if person.destination_time == self.time: # there is an error at time = 0
                self.en_route_list.remove(person)
                self.station.get_en_route_list().remove(person)
                current_vehicle_id = person.vehicle_id
                if current_vehicle_id is not None:
                    self.car_list.append(current_vehicle_id)
                if isinstance(person, classes.Employee):
                    person.reset()
                    self.employee_list.append(person)
                else:
                    del person
            else:
                break

    def assign_drivers(self):
        for destination in self.driver_requests:

            driver = self.station.employee_list[0]
            try:
                current_car = self.station.car_list.pop(0)
                driver = self.station.employee_list.pop(0)
                driver.update_status(self.station.station_id, destination, self.current_time, current_car)
                self.station_dict[driver.destination].append_en_route_list(driver)
            except IndexError:
                self.errors.append('No car for employee at Station Number {}'.format(driver.origin))
                self.no_car_emp_errors[self.current_time, driver.origin] += 1
                break


    def assign_pedestrians(self):
        for destination in pedestrian_tasks:
            ped = station.employee_list.pop(0)
            ped.update_status(station.station_id, destination, current_time)
            station_dictionary[ped.destination].append_en_route_list(ped)


    def update_customer_list(self, requests, time, cust_list):
        customer = classes.Person(requests[0], requests[1], time)
        cust_list.append(customer)


    def assign_customers(self, customer_list, cars, station_dictionary, errors, current_time):
        while len(customer_list) > 0:
            customer = customer_list[0]
            try:
                current_car = cars.pop(0)
                customer = customer_list.pop(0)
                customer.assign_cust_car(current_car)
                station_dictionary[customer.destination].append_en_route_list(customer)
            except IndexError:
                errors.append('No car for customer at Station Number {}'.format(customer.origin))
                self.no_car_cust_errors[current_time, customer.origin] += 1
                break
