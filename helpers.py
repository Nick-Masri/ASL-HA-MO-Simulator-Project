from classes import *


######################################
# Station Init ~ MC
######################################

def station_initializer(station_mapping_int, parking, employees_at_stations, cars_per_station=5):
    station_dict = {}
    car_count = 1
    for station in station_mapping_int.values():
        parkingSpots = parking[station]
        # Assign cars to the station.
        car_list = []
        for car in range(cars_per_station):
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


######################################
# Format and Load Instructions ~ NM / MC
######################################


def format_instructions(request):
    var = []
    count = 0
    for req in request:
        request_indices = np.nonzero(req)
        temp = []
        num_of_requests = len(request_indices[0])  # Number of (o, d) NOT the number of requests per (o, d)
        if num_of_requests > 0:
            for request in range(num_of_requests):
                origin = request_indices[0][request]
                destination = request_indices[1][request]
                for num in range(int(req[origin][destination])):  # Loop for number of custs going from (o, d)
                    temp.append((origin, destination))
                    count += 1
        var.append(temp)

    return var


