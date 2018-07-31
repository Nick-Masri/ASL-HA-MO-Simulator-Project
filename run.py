from helpers import format_instructions, Update
from smart import SmartController
import numpy as np

import matlab

smart = SmartController()
smart.run()
print(smart.station_ids)

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
    [tasks, output] = smart.controller.compute_rebalancing()
    print("Driver: {}".format(tasks['driverRebalancingQueue']))
    print("Vehicle: {}".format(tasks['vehicleRebalancingQueue']))
    # for k, v in output.items():
    #     print(k, v)

    driver_requests = tasks['vehicleRebalancingQueue']
    # driver_requests = [matlab.double([]), matlab.double([]), matlab.double([]), matlab.double([]), matlab.double([]), matlab.double([]), matlab.double([]), matlab.double([]), matlab.double([]), matlab.double([]), matlab.double([]), matlab.double([]), matlab.double([]), matlab.double([]), matlab.double([]), matlab.double([]), matlab.double([]), 14.0, matlab.double([]), matlab.double([]), matlab.double([]), matlab.double([]), matlab.double([]), matlab.double([]), matlab.double([]), matlab.double([]), matlab.double([]), matlab.double([]), matlab.double([]), matlab.double([]), matlab.double([]), matlab.double([]), matlab.double([]), matlab.double([]), matlab.double([]), matlab.double([]), matlab.double([]), matlab.double([]), matlab.double([]), matlab.double([]), matlab.double([]), matlab.double([]), matlab.double([]), matlab.double([]), matlab.double([]), matlab.double([]), matlab.double([]), matlab.double([]), matlab.double([]), matlab.double([]), matlab.double([]), matlab.double([]), matlab.double([]), matlab.double([]), matlab.double([]), matlab.double([]), matlab.double([]), matlab.double([])]
    pedestrian_requests = tasks['driverRebalancingQueue']

    for task in driver_requests:
        if task != matlab.double([]):
            print("Driver tasks: {}".format(task))

    for task in pedestrian_requests:
        if task != matlab.double([]):
            print("Ped tasks: {}".format(task))


for k, v in smart.station_dict.items():
    print("Station: {}, Num of cars: {}, Enroute_List: {}".format(k, len(v.car_list), len(v.en_route_list)))