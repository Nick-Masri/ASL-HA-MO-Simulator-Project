from simulator.update import Update

from simulator.output_formatting.overview import write, output
from simulator.output_formatting.measurement import Measurement

from simulator.setup import cust_requests, setup_vars


def run(controller):

    text, errors = [], []
    simulator = Update(controller, setup_vars)
    for time in range(len(cust_requests)):
        print('Time: {}'.format(time))

        customer_requests = cust_requests[time]

        errors, dict = simulator.loop(time, customer_requests)
        text.append(output(time, dict))

    # Creates an overview of the station at each time
    write("output_files/station_overview.txt", text)

    # Creates Heatmap images
    # heatmap_run(time, idle_vehicles, parking_per_station)

    # Creates graphs and a file full of measurements
    Measurement().record(errors, "output_files/measurements.txt")
