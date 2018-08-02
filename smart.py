from datetime import timedelta
import pandas as pd
import numpy as np

from classes import Station, Employee

from backend.controller import Controller


class SmartController:
    def __init__(self):
        self.stations = pd.read_csv('./data/stations_state.csv').set_index('station_id')
        # self.station_mapping = np.load('data/10_days/station_mapping.npy').item()
        self.station_ids = self.stations.index.tolist()
        self.n_stations = None
        self.station_dict = None
        self.controller = None
        self.station_dict = None
        self.vehicle_arrivals = None
        self.driver_arrivals = None
        self.idle_vehicles = None
        self.idle_drivers = None
        self.private_vehicles = np.zeros((58, 1))

        station_map = np.load('data/10_days/station_mapping.npy').item()
        self.station_mapping = {int(k): v for k, v in station_map.items()}

    def update_arrivals_and_idle(self, curr_time):
        self.vehicle_arrivals = np.zeros(shape=(self.n_stations, 12))
        self.driver_arrivals = np.zeros(shape=(self.n_stations, 12))

        idle_vehicles = []
        idle_drivers = []

        count = 0  # go through in the same order as the stations index
        for station in self.stations.index:
            # Update the driver and vehicle arrivals
            for person in self.station_dict[station].get_en_route_list(True):  # todo - This probably doesn't need to loop like this
                # print("Inside Person list Station: {}, person.destination_time = {}, curr_time: {}".format(station, person.destination_time, curr_time))
                for i in range(curr_time, curr_time + 12):
                    # print("i: {}, destination_time: {}".format(curr_time, person.destination_time))
                    # print(i == person.destination_time)
                    if int(person.destination_time) == i:
                        print("Curr time: {}, i: {}, vehichle.id".format(curr_time, i, person.vehicle_id))
                        if isinstance(person, Employee):
                            self.driver_arrivals[count][i - curr_time] += 1
                        if person.vehicle_id is not None:
                            print("Returning vehicle")
                            self.vehicle_arrivals[count][i - curr_time] += 1


            # Update the idle_vehicle and driver lists
            idle_vehicles.append(len(self.station_dict[station].car_list))
            idle_drivers.append(len(self.station_dict[station].employee_list))

            count += 1

        self.idle_vehicles = np.array(idle_vehicles)
        self.idle_drivers = np.array(idle_drivers)
        # print("Station: 55, idle_vehicles: {}".format(self.idle_vehicles)[17])
        # print("Station: 55, idle_drivers: {}".format(self.idle_drivers[17]))
        if self.driver_arrivals.max() > 0:
            print("Station: 55, driver_arrivals: {}".format(self.driver_arrivals.max()))
        if self.vehicle_arrivals.max() > 0:
            print("Station: 55, vehicle_arrivals: {}".format(self.vehicle_arrivals.max))



    def parse_ttimes(self, mode, stations, timestepsize):
        tt = pd.read_csv(
                'data/travel_times_matrix_'+mode+'.csv', index_col=0
            ).dropna(axis=0, how='all').dropna(axis=1, how='all')
        tt.columns = [int(c) for c in tt.columns]
        tt.iloc[:,:] = np.ceil(tt.values.astype(np.float64) / float(timestepsize.seconds))
        # reorder to match the index
        tt = tt.loc[stations.index][stations.index]  # QUESTION - Order them the same as the stations (random?)
        np.fill_diagonal(tt.values, 1)
        return tt

    def station_initializer(self, employees_at_stations, idx_type='real'):
        self.station_dict = {}
        car_count = 1
        # if idx_type == 'logical':  # TODO - FIX ME
        #     station_mapping = self.station_mapping.values
        for logical_station, station in enumerate(self.stations.index):  # TODO - Use the station.index or station_map here? - use idx_type to decide
            parkingSpots = self.stations['parking_spots'].get(station)
            # Assign cars to the station.
            car_list = []
            for car in range(self.stations['idle_vehicles'].get(station)):
                car_list.append(car_count)
                car_count += 1
            # Set up employee list
            emp_list = []
            if station in employees_at_stations.keys():
                for emp in range(employees_at_stations[station]):
                    emp_list.append(Employee(None, None, None))
            # Create the station
            self.station_dict[station] = Station(logical_station, parkingSpots, car_list, emp_list)


    def update_contoller(self,):
        forecast = {
            'vehicleArrivals': self.vehicle_arrivals,
            'driverArrivals': self.driver_arrivals
        }

        state = {
            'idleVehicles': self.idle_vehicles,
            'idleDrivers': self.idle_drivers,
            'privateVehicles': self.private_vehicles
        }
        print("Total Arrivals: {}".format(self.vehicle_arrivals.sum() + self.driver_arrivals.sum()))
        print("Total Idle: {}".format(self.idle_vehicles.sum() + self.idle_drivers.sum()))


        self.controller.update_state_arrivals(forecast, state)

    def run(self):
        # Get info about stations from the station csv
        station_ids = self.stations.index.tolist()
        self.n_stations = len(station_ids)

        # Create the station objects and dictionary
        employees_at_stations = {22: 2, 55: 2}

        self.station_initializer(employees_at_stations, 'real')
        for k,v in self.station_dict.items():
            print("Station: {}, Number of cars: {}".format(k, v.car_list))
        # Control Settings
        dt = 5 #         minutes
        timestepsize = timedelta(0, 60 * dt)  # in seconds
        horizon = timedelta(0, 12 * 60 * dt)  # in seconds
        thor = int(horizon.seconds / timestepsize.seconds)

        c_d = 10000.
        c_r = (1. / thor) * 0.0001 * 24. * c_d
        control_parameters = {}
        control_parameters['pvCap'] = 4.
        control_parameters['driverRebalancingCost'] = c_r
        control_parameters['vehicleRebalancingCost'] = c_r
        control_parameters['pvRebalancingCost'] = c_r
        control_parameters['lostDemandCost'] = c_d
        control_parameters['thor'] = float(int(horizon.seconds / timestepsize.seconds))

        modes = ['walk','hamo','car','bike']

        travel_times = {
            mode: self.parse_ttimes(mode, self.stations, timestepsize) for mode in modes
        }

        roadGraph = [list(range(1, self.n_stations + 1)) for i in range(self.n_stations)]

        road_network = {
            "roadGraph": roadGraph,
            "travelTimes": travel_times['hamo'].values,
            "driverTravelTimes": travel_times['walk'].values,
            "pvTravelTimes": travel_times['car'].values,
            "cTravelTimes": travel_times['car'].values,
            "parking": self.stations['parking_spots'].values
        }

        control_settings = {
            "RoadNetwork": road_network,
            "timestep_size": timestepsize,
            "station_ids": station_ids,
            "travel_times": travel_times,
            "horizon": horizon,
            "params": control_parameters,
            "stations": self.stations,
            "thor": int(horizon.seconds / timestepsize.seconds),
            "timezone_name": 'Asia/Tokoyo'
        }

        forecast_settings = {
            "day_forecast_path": 'data/mean_demand_weekday_5min.npy',
            "timestepsize": timestepsize,
            "horizon": 2 * int(horizon.seconds / timestepsize.seconds),
            "id_to_idx_path": "data/10_days/station_mapping.npy"  # QUESTION - how is this used? Maybe in the predict method of the NaiveForecaster Class?
        }

        self.controller = Controller(forecast_settings, control_settings)



if __name__ == "__main__":
    example = SmartController()
    example.run()
