import operator

##############################
# Stations Class ~ NM
##############################


class Station:
    def __init__(self, station_id, parking_spots, car_list, employee_list):
        self.station_id = station_id
        self.car_list = car_list
        self.parking_spots = parking_spots
        self.employee_list = employee_list
        self.en_route_list = []

    def get_en_route_list(self, is_sorted=False):  # sorted by destination_time, least to greatest
        if is_sorted:
            return sorted(self.en_route_list, key=operator.attrgetter('destination_time'))
        else:
            return self.en_route_list

    def get_en_route_drivers(self):
        en_route_drivers = 0
        for person in self.en_route_list:
            if person.vehicle_id is not None:
                en_route_drivers+=1

        return en_route_drivers

    def calc_parking(self):
        return self.parking_spots - len(self.car_list)