from simulator.update import Update
from simulator.output import write
from simulator.setup import station_initializer
from simulator.measurement import Measurement
from simulator.heatmap import heatmap_run

import math
import simulator.formatting as var

import numpy as np
###################
# Run Setup ~ NM
##################


def run(controller):
    station_dict = station_initializer(var.station_mapping_int, var.parking,
                                       var.employees_at_stations, var.cars_per_station)

    tool = Measurement()
    text = []
    # print(len(np.sum(var.cust_requests, axis=0)))
    for time in range(2880):
        # x = time / 28.79
        # if time % 100 == 0 or time == 2879:
        #     print("{}%".format(math.ceil(x)))

        print('Time: {}'.format(time))

        customer_requests = var.cust_requests[time]

        output, idle_vehicles, parking = Update(tool, controller, time, station_dict, customer_requests).loop()
        text.append(output)
        # if time % 6 == 0:
        #     heatmap_run(time, idle_vehicles, parking)

    write("files/station_overview.txt", text)
    print("\n\nfiles/station_overview.txt created")
    tool.record("files/measurements.txt")
    print("\nfiles/measurements.txt created")
