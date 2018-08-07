from helpers import format_instructions, Update
from smart import SmartController
import numpy as np

import matlab

smart = SmartController()

# Load cust requests
raw_requests = np.load('./data/10_days/hamo10days.npy')
cust_requests = format_instructions(raw_requests)

# Create lists for storing controller tasks
driver_requests = [[] for i in range(smart.n_stations)]
pedestrian_requests = [[] for i in range(smart.n_stations)]

# Initialize the simulator
update = Update(smart.travel_times)
for k, v in update.station_dict.items():
    if len(v.employee_list) > 0:
        print(k)

for curr_time in range(len(cust_requests)):
    print("Time: {}".format(curr_time))

    update.run(cust_requests[curr_time], curr_time)

    np.save('station_state2', update.error_dict)

    # Update the state of the Optimal Controller
    smart.update_arrivals_and_idle(curr_time, update.station_dict)
    smart.update_contoller()
    smart.controller.forecast_demand(curr_time)

    [tasks, output] = smart.controller.compute_rebalancing()

    # Print out information from controller solution
    for k, v in output.items():
        if k != 'cplex_out':
            print(k, v)

    # Updated the driver and pedestrican tasks in the simulator
    update.update_driver_ped_tasks(tasks['vehicleRebalancingQueue'], 'driver')
    update.update_driver_ped_tasks(tasks['driverRebalancingQueue'], 'pedestrian')

for k, v in smart.station_dict.items():
    print("Station: {}, Num of cars: {}, Enroute_List: {}".format(k, len(v.car_list), len(v.en_route_list)))