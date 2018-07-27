from datetime import timedelta
import pandas as pd
import numpy as np

from classes import Station, Employee

from backend.controller import Controller


class SmartController:
    def __init__(self):
        self.stations = pd.read_csv('./data/stations_state.csv').set_index('station_id')
        self.station_mapping = np.load('data/10_days/station_mapping.npy').item()
        self.controller = None

    def parse_ttimes(self, mode, stations, timestepsize):
        tt = pd.read_csv(
                'data/travel_times_matrix_'+mode+'.csv', index_col=0
            ).dropna(axis=0, how='all').dropna(axis=1, how='all')
        tt.columns = [int(c) for c in tt.columns]
        tt.iloc[:,:] = np.ceil(tt.values.astype(np.float64) / float(timestepsize.seconds))
        # reorder to match the index
        tt = tt.loc[stations.index][stations.index]  # QUESTION - This is where it get's reordered...why? It makes it out of order with parkng and other matrices
        np.fill_diagonal(tt.values, 1)
        return tt

    def station_initializer(self, employees_at_stations, idx_type='real'):
        station_dict = {}
        car_count = 1
        if idx_type == 'logical':
            station_mapping = self.station_mapping.values
        for station in self.stations.index:  # TODO - Use the station.index or station_map here?
            parkingSpots = self.stations['parking_spots'].get(int(station))
            # Assign cars to the station.
            car_list = []
            for car in range(self.stations['idle_vehicles'].get(int(station))):
                car_list.append(car_count)
                car_count += 1
            # Set up employee list
            emp_list = []
            if str(station) in employees_at_stations.keys():
                for emp in range(employees_at_stations[str(station)]):
                    emp_list.append(Employee(None, None, None))
            # Create the station
            station_dict[station] = Station(station, parkingSpots, car_list, emp_list)

        return station_dict

    def run(self):
        # Get info about stations from the station csv
        station_ids = self.stations.index.tolist()
        n_stations = len(station_ids)

        # Create the station objects and dictionary - TODO
        employees_at_stations = {'22': 2, '55': 2}  # TODO - decide if I'm using Real or logical station indices
        station_dict = self.station_initializer(employees_at_stations, 'real')

        # Control Settings
        dt = 5 # minutes
        timestepsize = timedelta(0, 60*dt) # in seconds
        horizon = timedelta(0, 12*60*dt) # in seconds
        thor = int(horizon.seconds / timestepsize.seconds)

        c_d = 10000.
        c_r = (1. / thor) * 0.0001 * 24. * c_d
        control_parameters = {}
        control_parameters['pvCap'] = 4.
        control_parameters['driverRebalancingCost'] = c_r
        control_parameters['vehicleRebalancingCost'] = c_r
        control_parameters['pvRebalancingCost'] = c_r
        control_parameters['lostDemandCost'] =  c_d
        control_parameters['thor'] = float(int(horizon.seconds / timestepsize.seconds))

        modes = ['walk','hamo','car','bike']

        travel_times = {
            mode: self.parse_ttimes(mode, self.stations, timestepsize) for mode in modes
        }

        roadGraph = [list(range(1, n_stations + 1)) for i in range(n_stations)]

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
