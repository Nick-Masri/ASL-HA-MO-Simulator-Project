from globals import *
import operator
from datetime import timedelta

######################################
# Creating Inheritance and Methods ~JS
######################################


car_travel_times = format_travel_times("./data/travel_times_matrix_car.csv", STATION_MAPPING, STATION_MAPPING_INT)
walking_travel_times = format_travel_times("./data/travel_times_matrix_walk.csv", STATION_MAPPING, STATION_MAPPING_INT)
hamo_travel_times = format_travel_times("./data/travel_times_matrix_hamo.csv", STATION_MAPPING, STATION_MAPPING_INT)

######################################
# Setting up roadgraphs in the format of the controller api w/real-station names
######################################

stations = pd.read_csv('./data/stations_state.csv').set_index('station_id')

station_ids = stations.index.tolist()
n_stations = len(station_ids)

dt = 5  # minutes
timestepsize = timedelta(0, 60 * dt)  # in seconds
horizon = timedelta(0, 12 * 60 * dt)  # in seconds
thor = int(horizon.seconds / timestepsize.seconds)

def parse_ttimes(mode, stations, timestepsize):
    tt = pd.read_csv(
        'data/travel_times_matrix_' + mode + '.csv', index_col=0
    ).dropna(axis=0, how='all').dropna(axis=1, how='all')
    tt.columns = [int(c) for c in tt.columns]
    tt.iloc[:, :] = np.ceil(tt.values.astype(np.float64) / float(timestepsize.seconds))
    # reorder to match the index
    tt = tt.loc[stations.index][stations.index]  # QUESTION - Order them the same as the stations (random?)
    np.fill_diagonal(tt.values, 1)
    return tt

modes = ['walk','hamo','car','bike']

travel_times = {
    mode: parse_ttimes(mode, stations, timestepsize) for mode in modes
}

station_mapping = np.load('data/10_days/station_mapping.npy').item()

############################################

class Person:
    def __init__(self, origin, destination, origin_time, vehicle_id=None):
        self.origin = origin
        self.destination = destination
        self.origin_time = origin_time
        if origin is None or destination is None or origin_time is None:
            self.destination_time = None
        else:
            # self.destination_time = origin_time + get_travel_time(car_travel_times, origin, destination)
            self.destination_time = origin_time + get_travel_time_pandas(travel_times['car'], origin, destination)
        self.current_position = [origin, destination]
        self.vehicle_id = vehicle_id

    def assign_cust_car(self, new_car=None):
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

    def update_status(self, origin, destination, origin_time, new_car=None):
        self.origin = origin
        self.destination = destination
        self.origin_time = origin_time
        self.vehicle_id = new_car
        if new_car is not None:
            # self.destination_time = origin_time + get_travel_time(hamo_travel_times, origin, destination)
            self.destination_time = origin_time + get_travel_time_pandas(travel_times['hamo'], origin, destination) # ADDED
        else:
            # self.destination_time = origin_time + get_travel_time(walking_travel_times, origin, destination)
            self.destination_time = origin_time + get_travel_time_pandas(travel_times['walk'], origin, destination)  # ADDED


class Station:
    def __init__(self, station_id, parking_spots, car_list=[], employee_list=[]):
        self.station_id = station_id
        self.car_list = car_list
        self.parking_spots = parking_spots
        self.available_parking = parking_spots - len(car_list)
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
    :param time_graph: The pandas Data Frame made for travel times
    :param origin: Where the car is traveling from
    :param destination: Where the car is going
    :return: Travel Time in minutes (rounded)
    """
    # I wonder if this could be more efficient. Maybe sort the time graph?

    # origin = STATION_MAPPING_INT[origin]
    # destination = STATION_MAPPING_INT[destination]

    if origin == destination:
        travel_time = 2
    else:
        travel_time = time_graph[origin][destination]

    return travel_time

def get_travel_time_pandas(time_graph, origin, destination):
    return int(time_graph.at[int(origin), int(destination)])


