class Assets:
    def __init__(self, asset_id,  current_position, status='IDLE', origin=-1, destination=-1, o_time=-1, d_time=-1):
        self.asset_id = asset_id # Employee ID number
        self.status = status # 0 = IDLE, 1 = en route, 2 = rebalancing
        self.origin = origin # IDLE = -1
        self.destination = destination # IDLE = -1
        self.o_time = o_time # IDLE = -1
        self.d_time = d_time # IDLE = -1
        self.current_position = current_position # if IDLE = current station number
    
    # Get Methods
    def get_id(self):
        return self.asset_id
    def get_status(self):
        return self.status
    def get_origin(self):
        return self.origin
    def get_destination(self):
        return self.destination
    def get_o_time(self):
        return self.o_time
    def get_d_time(self):
        return self.d_time
    def get_current_position(self):
        return self.current_position
    
    # Mutator Methods
    def change_status(self, s):
        self.status = s
    def change_origin(self, o):
        self.origin = o
    def change_destination(self, d):
        self.destination = d
    def change_o_time(self, ot):
        self.o_time = ot
    def change_d_time(self, dt):
        self.d_time = dt
    def change_current_position(self, cp):
        self.current_position = cp

class Station:
    def __init__(self, station_id, available_cars, waiting_customers='0'):
        self.station_id = station_id
        self.available_cars = available_cars
        self.waiting_customers = waiting_customers
    # Get Methods
    def get_id(self):
        return self.station_id
    def get_waiting_customers(self):
        return self.waiting_customers
    def get_available_cars(self):
        return self.available_cars
    
    # Mutator Methods
    def change_waiting_customers(self, wc):
        self.waiting_customers = wc
    def change_available_cars(self, ac):
        self.available_cars = ac


class CreateDict:
    def __init__(self, list):
        for x in list:
            [x[0]] = Assets(x[0], x[1])
        return dict
