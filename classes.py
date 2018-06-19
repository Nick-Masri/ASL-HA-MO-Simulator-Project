class Asset:
    def __init__(self, asset_id,  current_position, status='IDLE', origin=None, destination=None, o_time=None, d_time=None):
        self.asset_id = asset_id # Employee ID number
        self.status = status # 0 = IDLE, 1 = en route, 2 = rebalancing
        self.origin = origin # IDLE = None
        self.destination = destination # IDLE = None
        self.o_time = o_time # IDLE = None
        self.d_time = d_time # IDLE = None
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
    def __init__(self, station_id, available_cars=0, waiting_customers=0):
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


