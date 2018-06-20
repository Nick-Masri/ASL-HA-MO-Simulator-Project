import globals

class Person:
    def __init__(self, origin, destination, origin_time, destination_time, current_position, vehicle_id = None):
        self.origin = origin
        self.destination = destination
        self.origin_time = origin_time
        self.destination_time = origin_time + globals.GRAPH_VAR[origin][destination]
        self.current_position = current_position
        self.vehicle_id = vehicle_id
 
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
    def change_origin(self,o):
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
        
class Employee(Person):
    def __init__(self, origin, destination, origin_time, destination_time, current_position, vehicle_id = None, emp_id):
        Person.__init__(self, origin, destination, origin_time, destination_time, current_position, vehicle_id = None)
        self.emp_id = emp_id
    
    # Get Methods
    def get_origin(self):
        return self.origin
    def get_destination(self):
        return origin_time + globals.GRAPH_VAR[origin][destination]
    def get_origin_time(self):
        return self.origin_time
    def get_destination_time(self):
        return self.destination_time
    def get_current_position(self):
        return self.current_position
    def get_vehicle_id(self):
        return self.vehicle_id
    def get_emp_id(self):
        return self.emp_id
    
    # Mutator Methods
    def change_origin(self,o):
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
    def change_emp_id(self, e):
        self.emp_id = e
        
class Station:
    def __init__(self, station_id, cars, list_new_employees, list_waiting_customers, list_en_route):
        self.station_id = station_id
        self.cars = cars
        self.list_new_employees = list_new_employees
        self.list_waiting_customers = list_waiting_customers
        self.list_en_route = list_en_route

    # Get Methods
    def get_id(self):
        return self.station_id
    def get_cars(self):
        return self.cars
    def get_list_new_employees(self):
        return self.list_new_employees
    def get_list_waiting_customers(self):
        return self.list_waiting_customers
    def get_list_en_route(self):
        return self.list_en_route
    
    # Mutator Methods
    def change_cars(self, c):
        self.cars = c
    def change_list_new_employees(self, l):
        self.list_new_employees = l
    def change_list_waiting_customers(self, w):
        self.list_waiting_customers = w
    def change_list_en_route(self, er):
        self.list_en_route = er

