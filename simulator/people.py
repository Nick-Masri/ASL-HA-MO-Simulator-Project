from simulator.formatting import car_travel_times, walking_travel_times, hamo_travel_times


##############################
# People Classes ~ JS
##############################

class Person:
    def __init__(self, origin, destination, origin_time, vehicle_id=None):
        self.origin = origin
        self.destination = destination
        self.origin_time = origin_time
        self.car_travel_times = car_travel_times
        self.walking_travel_times = walking_travel_times
        self.hamo_travel_times = hamo_travel_times
        if origin is None or destination is None or origin_time is None:
            self.destination_time = None
        else:
            self.destination_time = origin_time + get_travel_time(self.car_travel_times, origin, destination)
        self.current_position = [origin, destination]
        self.vehicle_id = vehicle_id

    def update_status(self, request, new_car=None):
        self.origin = request[0]
        self.destination = request[1]
        self.origin_time = request[2]
        self.vehicle_id = new_car


class Employee(Person):
    def __init__(self, origin, destination, origin_time, vehicle_id=None):
        Person.__init__(self, origin, destination, origin_time, vehicle_id=None)

    def reset(self):
        self.origin = None
        self.destination = None
        self.origin_time = None
        self.destination_time = None
        self.vehicle_id = None

def get_travel_time(time_graph, origin, destination):
    if origin == destination:
        travel_time = 2
    else:
        travel_time = time_graph[origin][destination]
    return travel_time