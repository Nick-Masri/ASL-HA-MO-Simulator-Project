######################################
# Creating Functions For Update ~ NM
######################################


class Update:

    def __init__(self, current_time, station, station_dict, customer_requests, driver_requests, pedestrian_requests, errors):
        self.current_time = current_time
        self.station = station
        self.station_dict = station_dict
        self.customer_requests = customer_requests
        self.driver_requests = driver_requests
        self.pedestrian_requests = pedestrian_requests
        self.errors = errors

        self.employee_list = station.employee_list
        self.car_list = station.car_list

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
                no_car_emp_errors[current_time, driver.origin] += 1
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
                no_car_cust_errors[current_time, customer.origin] += 1
                break


    ######################################
    # Update Loop ~ NM
    ######################################


    def update(station_dict, customer_requests, current_time, driver_requests=[], pedestrian_requests=[]):
        errors = []
        for station in sorted(station_dict):  # Goes through the stations in order

            # For future efficiency check to see if there are any requests before doing all this work

            # Grab information relevant to this loop and organize
            current_station = station_dict[station]
            current_car_list = current_station.car_list
            employee_list = current_station.employee_list
            customer_list = current_station.get_waiting_customers(True)
            en_route_list = current_station.get_en_route_list(True)

            # Loop Arrivals
            arrivals(en_route_list, current_time, current_car_list, employee_list, current_station)

            # Check for Errors ******** This is assuming the capacity is 50 for each station ***********
            overload = 50 - (len(current_station.car_list) + len(current_station.get_en_route_list()))

            if overload < 0:
                errors.append("Station {0} will have {1} more cars than it can allow".format(current_station, -overload))
                no_park_errors[current_time, current_station] += 1

            # Put customers into cars
            if len(customer_requests) > 0:
                # Update Customer list and Assign Them
                for customer_request in customer_requests:
                    if customer_request[0] == station:
                        # add to station cust waiting list
                        update_customer_list(customer_request, current_time, customer_list)

                        print("CUSTOMER REQUEST: {}".format(customer_request))

                # assigns customers to cars if available
                assign_customers(customer_list, current_car_list, station_dict, errors, current_time)

            if len(driver_requests[station]) > 0 or len(pedestrian_requests[station]) > 0:
                # print('*****************************')
                # print('# of Driver Tasks: {}'.format(len(driver_requests[station])))
                # print('# of Ped Tasks: {}'.format(len(pedestrian_requests[station])))
                # print('*****************************')

                # Assign drivers
                # Update employee object and add it to destination enroute list
                assign_drivers(current_station, driver_requests[station], station_dict, errors, current_time)

                # Assign Pedestrians
                # Update employee object and add it to destination enroute list (no car and time travel)
                assign_pedestrians(current_station, pedestrian_requests[station], station_dict, current_time)

        return errors