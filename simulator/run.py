from simulator.update import Update

from simulator.output.overview import write
from simulator.output.measurement import Measurement

from simulator.setup import cust_requests, travel_times, setup_vars


def run(controller):

    tool = Measurement()
    text = []

    for time in range(2880):
        # x = time / 28.79
        # if time % 100 == 0 or time == 2879:
        #     print("{}%".format(math.ceil(x)))

        print('Time: {}'.format(time))

        customer_requests = cust_requests[time]

        output, idle_vehicles, parking = Update(tool, controller, time, customer_requests, travel_times, setup_vars).loop()
        text.append(output)
        # if time % 6 == 0:
        #     heatmap_run(time, idle_vehicles, parking_per_station)

    write("files/station_overview.txt", text)
    print("\n\nfiles/station_overview.txt created")
    tool.record("files/measurements.txt")
    print("\nfiles/measurements.txt created")
