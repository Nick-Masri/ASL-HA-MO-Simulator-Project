from globals import *
import operator


class Person:
    def __init__(self, origin, destination, origin_time, vehicle_id=None):
        self.origin = origin
        self.destination = destination
        self.origin_time = origin_time
        if origin is None or destination is None or origin_time is None:
            self.destination_time = None
        else:
            self.destination_time = origin_time + get_travel_time(CAR_TRAVEL_TIMES, origin, destination)
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
        self.origin = request.get_origin()
        self.destination = request.get_destination()
        self.origin_time = request.get_origin_time()
        self.current_position = [request.get_origin(), request.get_destination()]
        self.vehicle_id = new_car


class Employee(Person):
    def __init__(self, origin, destination, origin_time, employee_id, vehicle_id=None):
        Person.__init__(self, origin, destination, origin_time, vehicle_id=None)
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
        self.destination_time = None
        self.vehicle_id = None


class Station:
    def __init__(self, station_id, car_list=[], employee_list=[]):
        self.station_id = station_id
        self.car_list = car_list
        self.employee_list = employee_list
        self.en_route_list = []
        self.waiting_customers = []
        self.request_list = []

    # Get Methods
    def get_id(self):
        return self.station_id

    def get_car_list(self):
        return self.car_list

    def get_employee_list(self):
        return self.employee_list

    def get_waiting_customers(self, is_sorted=False):  # sorted by origin_time, least to greatest
        if is_sorted:
            return sorted(self.waiting_customers, key=operator.attrgetter('origin_time'))
        else:
            return self.waiting_customers

    def get_en_route_list(self, is_sorted=False):  # sorted by destination_time, least to greatest
        if is_sorted:
            return sorted(self.en_route_list, key=operator.attrgetter('destination_time'))
        else:
            return self.en_route_list

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

    def append_en_route_list(self, employee):
        self.en_route_list.append(employee)

    def append_waiting_customers(self, customer):
        self.waiting_customers.append(customer)


def get_travel_time(time_graph, origin, destination):
    """
    little function for finding the value in a travel time graph
    :param time_graph: The padas Data Frame made for travel times
    :param origin: Where the car is traveling from
    :param destination: Where the car is going
    :return: Travel Time in minutes (rounded)
    """
    # I wonder if this could be more efficient. Maybe sort the time graph?

    # origin = STATION_MAPPING_INT[origin]
    # destination = STATION_MAPPING_INT[destination]
    if origin == destination:
        travel_time = 5
    else:
        travel_time = time_graph[origin][destination]
        travel_time = int(round(travel_time/60))
    return travel_time


station_5 = [req for req in CUST_REQUESTS if len(req) > 0]
station_5 = [[req, get_travel_time(CAR_TRAVEL_TIMES, req[0][0], req[0][1])] for req in station_5 if req[0][1] == 5]

# for req in station_5:
#     print(req)