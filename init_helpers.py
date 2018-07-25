from classes import *


def station_initializer(station_mapping_int, parking, employees_at_stations, cars):
    station_dict = {}
    car_count = 1
    for station in station_mapping_int.values():
        parkingSpots = parking[station]
        # Assign cars to the station.
        car_list = []
        for car in range(cars[station]):
            car_list.append(car_count)
            car_count += 1
        # Set up employee list
        emp_list = []
        if station in employees_at_stations.keys():
            for emp in range(employees_at_stations[station]):
                emp_list.append(Employee(None, None, None))
        # Create the station
        station_dict[station] = Station(station, parkingSpots, car_list, emp_list)

    return station_dict
