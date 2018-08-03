from helpers import format_instructions, Update
from smart import SmartController
import numpy as np

import matlab

smart = SmartController()
smart.initialize()

raw_requests = np.load('./data/10_days/hamo10days.npy')
cust_requests = format_instructions(raw_requests)
driver_requests = [[] for i in range(smart.n_stations)]
pedestrian_requests = [[] for i in range(smart.n_stations)]

update = Update(smart.station_mapping, smart.station_ids, smart.station_dict, smart.travel_times)



for curr_time in range(len(cust_requests)):
    print("Time: {}".format(curr_time))

    cust_request = cust_requests[curr_time]

    update.run(smart.station_dict, cust_request, curr_time)

    np.save('station_state2', update.error_dict)

    smart.update_arrivals_and_idle(curr_time)
    smart.update_contoller()
    smart.controller.forecast_demand(curr_time)

    [tasks, output] = smart.controller.compute_rebalancing()

    for k, v in output.items():
        if k != 'cplex_out':
            print(k, v)


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