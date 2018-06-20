import globals
from operator import itemgetter


class Person:
    def __init__(self, origin, destination, origin_time, current_position, vehicle_id=None):
        self.origin = origin
        self.destination = destination
        self.origin_time = origin_time
        self.destination_time = origin_time + globals.GRAPH_VAR[origin][destination]
        self.current_position = current_position
        self.vehicle_id = vehicle_id

    # Get Methods
    def get_origin(self):
        return self.origin

    def get_destination(self):
        return self.destination

    def get_origin_time(self):
        return self.origin_time

    def get_destination_time(self):
        return self.destination_time

    def get_current_position(self):
        return self.current_position

    def get_vehicle_id(self):
        return self.vehicle_id

    # Mutator Methods
    def change_origin(self, o):
        self.origin = o

    def change_destination(self, d):
        self.destination = d

    def change_origin_time(self, ot):
        self.origin_time = ot

    def change_destination_time(self, dt):
        self.destination_time = dt

    def change_current_position(self, cp):
        self.current_position = cp

    def change_vehicle_id(self, v):
        self.vehicle_id = v


class Employee(Person):
    def __init__(self, origin, destination, origin_time, destination_time, current_position, vehicle_id=None,
                 employee_id):
        Person.__init__(self, origin, destination, origin_time, destination_time, current_position, vehicle_id=None)
        self.employee_id = employee_id

    # Get Methods
    def get_origin(self):
        return self.origin

    def get_destination(self):
        return origin_time + globals.GRAPH_VAR[origin][destination]

    def get_origin_time(self):
        return self.origin_time

    def get_destination_time(self):
        return self.destination_time

    def get_current_position(self):
        return self.current_position

    def get_vehicle_id(self):
        return self.vehicle_id

    def get_employee_id(self):
        return self.employee_id

    # Mutator Methods
    def change_origin(self, o):
        self.origin = o

    def change_destination(self, d):
        self.destination = d

    def change_origin_time(self, ot):
        self.origin_time = ot

    def change_destination_time(self, dt):
        self.destination_time = dt

    def change_current_position(self, cp):
        self.current_position = cp

    def change_vehicle_id(self, v):
        self.vehicle_id = v

    def change_employee_id(self, e):
        self.employee_id = e

    # Unique Methods
    def reset(self):
        self.current_position = self.destination
        self.origin = None
        self.destination = None
        self.origin_time = None
        self.vehicle_id = None


class Station:
    def __init__(self, station_id, cars, employee_list, waiting_customers, en_route_list, request_list):
        self.station_id = station_id
        self.cars = cars
        self.employee_list = employee_list
        self.waiting_customers = waiting_customers
        self.en_route_list = en_route_list
        self.request_list = request_list

    # Get Methods
    def get_id(self):
        return self.station_id

    def get_cars(self):
        return self.cars

    def get_employee_list(self):
        return self.employee_list

    def get_waiting_customers(self):  # sorted by origin_time, least to greatest
        return sorted(self.waiting_customers, key=itemgetter(2))

    def get_en_route_list(self):  # sorted by destination_time, least to greatest
        return sorted(self.en_route_list, key=itemgetter(3))

    def get_request_list(self):
        return self.request_list

    # Mutator Methods
    def change_cars(self, c):
        self.cars = c

    def change_employee_list(self, el):
        self.employee_list = el

    def change_waiting_customers(self, cr):
        self.waiting_customers = cr

    def change_en_route_list(self, er):
        self.en_route_list = er

    def change_request_list(self, rl):
        self.request_list = rl

    # Unique Methods
    def assign_employee(self):
        pass