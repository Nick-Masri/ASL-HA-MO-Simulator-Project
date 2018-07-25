from simulator.update import Update
from simulator.output import write
from simulator.setup import station_initializer

import simulator.formatting as var


def run(controller):

    station_dict = station_initializer(var.station_mapping_int, var.parking,
                                       var.employees_at_stations, var.cars_per_station)
    text = []
    for time in range(2880):
        print("Time: {}".format(time))

        customer_requests = var.cust_requests[time]

        time_stamp = Update(controller, time, station_dict, customer_requests).loop()
        text.append(time_stamp)

    write("output.txt", text)
    print("\n\nOutput.txt created")