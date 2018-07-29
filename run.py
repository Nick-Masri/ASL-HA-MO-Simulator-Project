from helpers import update, format_instructions
from smart import SmartController
import numpy as np

smart = SmartController()
smart.run()

raw_requests = np.load('./data/10_days/hamo10days.npy')
cust_requests = format_instructions(raw_requests)
driver_requests = [[] for i in range(smart.n_stations)]
driver_requests = [[] for i in range(smart.n_stations)]
pedestrian_requests = [[] for i in range(smart.n_stations)]

for curr_time in range(60, len(cust_requests)):
    print("Time: {}".format(curr_time))

    errors = update(smart.station_dict, cust_requests[curr_time], curr_time, smart.station_mapping, driver_requests, pedestrian_requests)
    smart.update_arrivals_and_idle(curr_time)
for k, v in smart.station_dict.items():
    print("Station: {}, Num of cars: {}, Enroute_List: {}".format(k, len(v.car_list), len(v.en_route_list)))