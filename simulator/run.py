from simulator.update import Update

from simulator.output.overview import write
from simulator.output.measurement import Measurement

from simulator.setup import cust_requests, setup_vars


def run(controller):

    tool = Measurement()
    text = []
    simulator = Update(controller, setup_vars)
    for time in range(2880):
        print('Time: {}'.format(time))

        customer_requests = cust_requests[time]

        errors = simulator.loop(time, customer_requests)
        # text.append(output)
        # tool.write()
        # # if time % 6 == 0:
        #     heatmap_run(time, idle_vehicles, parking_per_station)

    write("files/station_overview.txt", text)
    print("\n\nfiles/station_overview.txt created")
    tool.record("files/measurements.txt")
    print("\nfiles/measurements.txt created")
