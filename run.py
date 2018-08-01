from helpers import format_instructions, Update
from smart import SmartController
import numpy as np

import matlab

smart = SmartController()
smart.run()

raw_requests = np.load('./data/10_days/hamo10days.npy')
cust_requests = format_instructions(raw_requests)
driver_requests = [[] for i in range(smart.n_stations)]
pedestrian_requests = [[] for i in range(smart.n_stations)]

update = Update(smart.station_mapping, smart.station_ids)

for curr_time in range(70, len(cust_requests)):
    print("Time: {}".format(curr_time))

    errors = update.run(smart.station_dict, cust_requests[curr_time], curr_time,  smart.stations, driver_requests, pedestrian_requests)
    smart.update_arrivals_and_idle(curr_time)
    smart.update_contoller()
    smart.controller.forecast_demand(curr_time)
    # Create lots of demand from station 2008 (30) --> 48 (32)
    fake_demand = np.zeros((58,58,24))
    fake_demand[30][32] = np.ones((1,24))
    fake_demand[30][32][23] = 12.
    smart.controller.forecast['demand'] = fake_demand
    print(smart.controller.forecast['demand'].shape)
    [tasks, output] = smart.controller.compute_rebalancing()

    for k, v in output.items():
        if k != 'cplex_out':
            print(k, v)

    driver_requests = tasks['vehicleRebalancingQueue']
    # driver_requests = [matlab.double([]), matlab.double([]), matlab.double([]), matlab.double([]), matlab.double([]), matlab.double([]), matlab.double([]), matlab.double([]), matlab.double([]), matlab.double([]), matlab.double([]), matlab.double([]), matlab.double([]), matlab.double([]), matlab.double([]), matlab.double([]), matlab.double([]), 14.0, matlab.double([]), matlab.double([]), matlab.double([]), matlab.double([]), matlab.double([]), matlab.double([]), matlab.double([]), matlab.double([]), matlab.double([]), matlab.double([]), matlab.double([]), matlab.double([]), matlab.double([]), matlab.double([]), matlab.double([]), matlab.double([]), matlab.double([]), matlab.double([]), matlab.double([]), matlab.double([]), matlab.double([]), matlab.double([]), matlab.double([]), matlab.double([]), matlab.double([]), matlab.double([]), matlab.double([]), matlab.double([]), matlab.double([]), matlab.double([]), matlab.double([]), matlab.double([]), matlab.double([]), matlab.double([]), matlab.double([]), matlab.double([]), matlab.double([]), matlab.double([]), matlab.double([]), matlab.double([])]
    pedestrian_requests = tasks['driverRebalancingQueue']
    # pedestrian_requests = [matlab.double([]), matlab.double([]), matlab.double([]), matlab.double([]), matlab.double([]), matlab.double([]), matlab.double([]), matlab.double([]), matlab.double([]), matlab.double([]), matlab.double([]), matlab.double([]), matlab.double([]), 15.0, matlab.double([]), matlab.double([]), matlab.double([]), matlab.double([]), matlab.double([]), matlab.double([]), matlab.double([]), matlab.double([]), matlab.double([]), matlab.double([]), matlab.double([]), matlab.double([]), matlab.double([]), matlab.double([]), matlab.double([]), matlab.double([]), matlab.double([]), matlab.double([]), matlab.double([]), matlab.double([]), matlab.double([]), matlab.double([]), matlab.double([]), matlab.double([]), matlab.double([]), matlab.double([]), matlab.double([]), matlab.double([]), matlab.double([]), matlab.double([]), matlab.double([]), matlab.double([]), matlab.double([]), matlab.double([]), matlab.double([]), matlab.double([]), matlab.double([]), matlab.double([]), matlab.double([]), matlab.double([]), matlab.double([]), matlab.double([]), matlab.double([]), matlab.double([])]
    print("Ped: {}".format(pedestrian_requests))
    print("Vehicle: {}".format(driver_requests))

    update.update_driver_ped_tasks(tasks['vehicleRebalancingQueue'], 'driver')
    update.update_driver_ped_tasks(tasks['driverRebalancingQueue'], 'pedestrian')

    for station, task in enumerate(driver_requests):
        if task != matlab.double([]):
            print("Logical Station: {}, Driver tasks: {}".format(station, task))

    for station, task in enumerate(pedestrian_requests):
        if task != matlab.double([]):
            print("Logical Station: {}, Ped tasks: {}".format(station, task))


for k, v in smart.station_dict.items():
    print("Station: {}, Num of cars: {}, Enroute_List: {}".format(k, len(v.car_list), len(v.en_route_list)))