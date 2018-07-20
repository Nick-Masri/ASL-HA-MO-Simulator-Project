from globals import *
import operator

######################################
# Creating Inheritance and Methods ~JS
######################################


car_travel_times = format_travel_times("./data/travel_times_matrix_car.csv", STATION_MAPPING, STATION_MAPPING_INT)

class Person:
    def __init__(self, origin, destination, origin_time, vehicle_id=None):
        self.origin = origin
        self.destination = destination
        self.origin_time = origin_time
        if origin is None or destination is None or origin_time is None:
            self.destination_time = None
        else:
            self.destination_time = origin_time + get_travel_time(car_travel_times, origin, destination)
        self.current_position = [origin, destination]
        self.vehicle_id = vehicle_id

    def update_status(self, request, new_car=None):
        self.origin = request.origin
        self.destination = request.destination
        self.origin_time = request.origin_time
        self.vehicle_id = new_car


class Employee(Person):
    def __init__(self, origin, destination, origin_time, vehicle_id=None):
        Person.__init__(self, origin, destination, origin_time, vehicle_id=None)

    # Unique Methods
    def reset(self):
        self.origin = None
        self.destination = None
        self.origin_time = None
        self.destination_time = None
        self.vehicle_id = None


class Station:
    def __init__(self, station_id, parking_spots, car_list=[], employee_list=[]):
        self.station_id = station_id
        self.car_list = car_list
        self.parking_spots = parking_spots
        self.availble_parking = parking_spots - len(car_list)
        self.employee_list = employee_list
        self.en_route_list = []
        self.waiting_customers = []
        self.request_list = []

    # Get Methods
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
    
    # Unique Methods

    def append_en_route_list(self, employee):
        self.en_route_list.append(employee)

    def append_waiting_customers(self, customer):
        self.waiting_customers.append(customer)

######################################
# Travel Time Assignments ~ MC
######################################

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