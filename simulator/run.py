from simulator.update import Update

from simulator.output_formatting.overview import write, output
from simulator.output_formatting.measurement import Measurement
from simulator.output_formatting.heatmap import heatmap_run

from simulator.setup import cust_requests, setup_vars


def run(controller):

    text, errors, log = [], [], []
    simulator = Update(controller, setup_vars)
    for time in range(len(cust_requests)):
        print('Time: {}'.format(time))

        customer_requests = cust_requests[time]

        log, dict = simulator.loop(time, customer_requests)
        text.append(output(time, dict))

    # Creates an overview of the station at each time
    write("output_files/station_overview.txt", text)

    # Creates graphs and a file full of measurements
    Measurement().record(log, "output_files/measurements.txt")

    # Creates Heatmap images, currently runs for only one day
    # heatmap_run(log)
