import globals
from operator import itemgetter


class Person:
    def __init__(self, origin, destination, origin_time, vehicle_id=None):
        self.origin = origin
        self.destination = destination
        self.origin_time = origin_time
        self.destination_time = origin_time + globals.GRAPH_VAR[origin][destination]
        self.current_position = [origin, destination]
        self.vehicle_id = vehicle_id

    # comparison methods
    def __eq__(self, other):
        """Override the default Equals behavior"""
        return (self.origin == other.get_origin()
                and self.destination == other.get_destination()
                and self.origin_time == other.get_origin_time()
                and self.current_position == other.get_current_position()
                and self.vehicle_id == other.get_vehicle_id()
                )

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

    def update_status(self, request, new_car=None):
        self.origin = request[0]
        self.destination = request[1]
        self.origin_time = request[2]
        self.current_position = [request[0], request[1]]
        self.vehicle_id = new_car


class Employee(Person):
    def __init__(self, origin, destination, origin_time, employee_id, vehicle_id=None):
        Person.__init__(self, origin, destination, origin_time, vehicle_id)
        self.employee_id = employee_id

    # comparison methods
    def __eq__(self, other):
        """Override the default Equals behavior"""
        return (self.origin == other.get_origin()
                and self.destination == other.get_destination()
                and self.origin_time == other.get_origin_time()
                and self.current_position == other.get_current_position()
                and self.vehicle_id == other.get_vehicle_id()
                and self.employee_id == other.get_employee_id()
                )

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
    def __init__(self, station_id, car_list, employee_list):
        self.station_id = station_id
        self.car_list = car_list
        self.employee_list = employee_list
        self.waiting_customers = None
        self.en_route_list = None
        self.request_list = None

    # Get Methods
    def get_id(self):
        return self.station_id

    def get_car_list(self):
        return self.car_list

    def get_employee_list(self):
        return self.employee_list

    def get_waiting_customers(self):  # sorted by origin_time, least to greatest
        return sorted(self.waiting_customers, key=itemgetter(2))

    def get_enroute_list(self):  # sorted by destination_time, least to greatest
        return sorted(self.en_route_list, key=itemgetter(3))

    def append_enroute_list(self, employee):
        self.get_enroute_list().append(employee)

    def get_request_list(self):
        return self.request_list

    # Mutator Methods
    def change_car_list(self, c):
        self.car_list = c

    def change_employee_list(self, el):
        self.employee_list = el

    def change_waiting_customers(self, cr):
        self.waiting_customers = cr

    def change_en_route_list(self, er):
        self.en_route_list = er

    def change_request_list(self, rl):
        self.request_list = rl

    # Unique Methods

