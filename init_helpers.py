from classes import *


def station_initializer(station_mapping, stations, employees_at_stations, idx_type='real'):
    station_dict = {}
    car_count = 1
    if idx_type == 'logical':
        station_mapping = station_mapping.values
    for station in stations.index:  # TODO - Use the station.index or station_map here?
        parkingSpots = stations['parking_spots'].get(int(station))
        # Assign cars to the station.
        car_list = []
        for car in range(stations['idle_vehicles'].get(int(station))):
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
