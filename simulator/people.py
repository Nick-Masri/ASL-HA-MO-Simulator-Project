from simulator.setup import travel_times


def get_travel_time(time_graph, origin, destination):

    return int(time_graph.at[int(origin), int(destination)])


class Person:
    def __init__(self, origin, destination, origin_time, vehicle_id):
        self.origin = origin
        self.destination = destination
        self.origin_time = origin_time
        self.destination_time = origin_time + get_travel_time(travel_times['hamo'], origin, destination)
        self.vehicle_id = vehicle_id

    def update_status(self, origin, destination, origin_time, new_car):
        self.origin = origin
        self.destination = destination
        self.origin_time = origin_time
        self.vehicle_id = new_car
        self.destination_time = origin_time + get_travel_time(travel_times['hamo'], origin, destination)


class Employee:
    def __init__(self, origin, destination, origin_time, vehicle_id=None):
        self.origin = origin
        self.destination = destination
        self.origin_time = origin_time
        self.vehicle_id = vehicle_id
        self.destination_time = None

    def reset(self):
        self.origin = None
        self.destination = None
        self.origin_time = None
        self.destination_time = None
        self.vehicle_id = None

    def update_status(self, origin, destination, origin_time, new_car=None):
        self.origin = origin
        self.destination = destination
        self.origin_time = origin_time
        self.vehicle_id = new_car
        if new_car is not None:
            self.destination_time = origin_time + get_travel_time(travel_times['hamo'], origin, destination)
        else:
            self.destination_time = origin_time + get_travel_time(travel_times['walk'], origin, destination)


