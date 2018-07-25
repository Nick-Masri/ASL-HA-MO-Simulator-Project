import simulator.update
import simulator.parameters
import simulator.helpers
import simulator.output



def run(controller):

    errors = simulator.update(controller, station_dict, customer_requests, time, driver_requests, pedestrian_requests)


        for time in range(2880):
            print("Time: {}".format(time))

            idle_vehicles = []
            idle_drivers = []

            vehicle_arrivals = np.zeros(shape=(len(station_dict), 12))
            driver_arrivals = np.zeros(shape=(len(station_dict), 12))

            customer_requests = cust_requests[time]


            for station in sorted(station_dict):




            elif controller_type == 'naive':

                if morningStart <= time and time <= morningEnd:
                    morning_rebalancing(station_dict)
                    morningStart += 24
                    morningEnd += 24
                elif eveningStart <= time and time <= eveningEnd:
                    evening_rebalancing(station_dict)
                    eveningStart += 24
                    eveningEnd += 24


            pedestrian_requests = tasks['driverRebalancingQueue']
            # for request in pedestrian_requests:
            #     print(request)
            vehicle_requests = tasks['vehicleRebalancingQueue']
