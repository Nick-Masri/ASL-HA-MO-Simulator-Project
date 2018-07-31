from simulator.update import Update
from simulator.output import write
from simulator.setup import station_initializer
from simulator.measurement import Measurement

import math
import simulator.formatting as var


###################
# Run Setup ~ NM
##################

def run(controller):
    station_dict = station_initializer(var.station_mapping_int, var.parking,
                                       var.employees_at_stations, var.cars_per_station)

    tool = Measurement()
    text = []
    for time in range(2880):
        # x = time / 28.79
        # if time % 100 == 0 or time == 2879:
        #     print("{}%".format(math.ceil(x)))

        print('Time: {}'.format(time))

        customer_requests = var.cust_requests[time]

        time_stamp = Update(tool, controller, time, station_dict, customer_requests).loop()
        text.append(time_stamp)

        

    write("files/output.txt", text)
    print("\n\nfiles/output.txt created")
    tool.record("files/errors.txt")
    print("\nfiles/errors.txt created")
