import operator

##############################
# Stations Class ~ NM
##############################

class Station:
    def __init__(self, station_id, parking_spots, car_list=[], employee_list=[]):
        self.station_id = station_id
        self.car_list = car_list
        self.parking_spots = parking_spots
        self.employee_list = employee_list
        self.en_route_list = []
        self.waiting_customers = []
        self.request_list = []

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

    def append_en_route_list(self, employee):
        self.en_route_list.append(employee)

    def append_waiting_customers(self, customer):
        self.waiting_customers.append(customer)

    def calc_parking(self):
        return self.parking_spots - len(self.car_list)

