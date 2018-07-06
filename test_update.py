from helpers import update
from classes import *
from globals import CAR_TRAVEL_TIMES

def station_test(origin, destination, cust_requests=[]):
    travel_time = get_travel_time(CAR_TRAVEL_TIMES, origin, destination)

    station_list = {origin: Station(origin, [x for x in range(5)]), destination: Station(destination, [x for x in range(6, 11)])}
    if len(cust_requests) == 0:
        cust_requests = [[[origin, destination]] for _iter in range(5)]

    print('Customer Requests: {}'.format(cust_requests))
    for time in range(len(cust_requests)):
        curr_customer_requests = cust_requests[time]
        errors = update(station_list, [], [], curr_customer_requests, time)

    # Checks the number of enroute vehicles
    assert len(station_list[destination].get_en_route_list()) == 5
    count = len(station_list[destination].get_car_list())

    # After travel time make sure there it's adding the number of cars that should be arriving each minute
    more_requests = [[] for _iter in range(6)]
    for time in range(len(more_requests)):
        # time = curr time + travel_time (-1 to account for time 1 = index 0
        update(station_list, [], [], more_requests[time], time+travel_time-1)

        assert count == len(station_list[destination].get_car_list())
        try:
            count += len(cust_requests[time])
        except:
            print("No more customer requests")


def test_station_1_2():
    station_test(1, 2)


def test_station_1_1():
    station_test(1, 1)


def test_multiple_requests_pre_min():
    origin = 1
    destination = 2
    travel_time = get_travel_time(CAR_TRAVEL_TIMES, origin, destination)
    station_list = {origin: Station(origin, [x for x in range(20)]),
                    destination: Station(destination, [x for x in range(6, 11)])}
    cust_requests = [[[1, 2], [1, 2], [1, 2], [1, 2]], [[1, 2]], [[1, 2]], [[1, 2]]]

    for time in range(len(cust_requests)):
        curr_customer_requests = cust_requests[time]
        # print(curr_customer_requests)
        errors = update(station_list, [], [], curr_customer_requests, time)
        print(len(station_list[destination].get_en_route_list()))
        print(len(station_list[destination].get_car_list()))

    # Checks the number of enroute vehicles
    assert len(station_list[destination].get_en_route_list()) == 7

    count = 5

    # After travel time make sure there it's adding the number of cars that should be arriving each minute
    more_requests = [[] for _iter in range(6)]
    for time in range(len(cust_requests)):
        # time = curr time + travel_time (-1 to account for time 1 = index 0
        update(station_list, [], [], more_requests[time], time + travel_time - 1)
        assert count == len(station_list[destination].get_car_list())
        try:
            count += len(cust_requests[time])
        except:
            print("No more customer requests")