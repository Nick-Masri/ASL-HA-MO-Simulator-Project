from simulator.update import Update
import simulator.formatting


def run(controller):

    for time in range(2880):
        print("Time: {}".format(time))

        station_dict = simulator.formatting.station_dict
        driver_requests = [[] for i in range(len(station_dict))]
        pedestrian_requests = [[] for i in range(len(station_dict))]
        customer_requests = simulator.formatting.cust_requests[time]

        errors = Update(controller, station_dict, customer_requests, time)