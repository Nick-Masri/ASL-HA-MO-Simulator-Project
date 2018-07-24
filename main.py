#!/usr/bin/python
from simulator import state_tracker
from simulator import

# Setting up Station Mapping ~ MC
station_mapping_int = {int(k): v for k, v in station_mapping.items()}

# Formatting Data ~ NM
car_travel_times = format_travel_times(car_data, station_mapping, station_mapping_int)
walking_travel_times = format_travel_times(walking_data, station_mapping, station_mapping_int)
hamo_travel_times = format_travel_times(hamo_data, station_mapping, station_mapping_int)
mean_demand = np.load(mean_data)

# Demand Forecaster ~ MC
time_length = mean_demand.shape[0]
station_length = mean_demand.shape[1]
demand_forecast_alt = demand_forecast_formatter(station_length, time_length, mean_demand)

# Setting up parking ~ NM
parking_csv = pd.read_csv(parking_data).iloc[:, parking_columns]
locations = parking_csv.values

parking = {}
for item in locations:
    parking[station_mapping_int[item[0]]] = item[1]

station_dict = station_initializer(station_mapping_int, parking, employees_at_stations, cars_per_station)



######################################
# Main Loop ~ NM
######################################


raw_requests = np.load('./data/10_days/hamo10days.npy')
cust_requests = format_instructions(raw_requests)
driver_requests = [[] for i in range(len(station_dict))]
pedestrian_requests = [[] for i in range(len(station_dict))]

for time in range(0, len(cust_requests)):
    print("Time: {}".format(time))
    text_file_output.append("\nTime: {}".format(time))
    text_file_output.append('------------------------------------------------------')

    idle_vehicles = []
    idle_drivers = []

    vehicle_arrivals = np.zeros(shape=(len(station_dict), 12))
    driver_arrivals = np.zeros(shape=(len(station_dict), 12))

    customer_requests = cust_requests[time]

    errors = main.Update(station_dict, customer_requests, time, driver_requests, pedestrian_requests)
    # for station in station_dict:
    #     print('******************')
    #     print(station_dict[station].car_list)
    #     print('*******************')
    # Logging current state
    for station in sorted(station_dict):

        ######################################
        # Writing to text_file_output Files ~ NM
        ######################################

        text_file_output.append('\tStation: {}'.format(station))
        text_file_output.append('\t\tNumber of Idle Vehicles: {}'.format(len(station_dict[station].car_list)))
        text_file_output.append('\t\tAvailable Parking: {}'.format(50 - len(station_dict[station].car_list)))
        text_file_output.append('\t\tNum People En_Route: {}'.format(len(station_dict[station].get_en_route_list())))

        ############################################
        # Setting Up Idle Vehicles and Drivers ~ JS
        ############################################

        idle_vehicles.append(len(station_dict[station].car_list))
        idle_drivers.append(len(station_dict[station].employee_list))

        ########################################
        # Updating Vehicle/Driver Arrivals ~ NM
        ########################################

        for person in station_dict[station].get_en_route_list(True):
            for i in range(time, time + 12):
                # if person.vehicle_id is not None:
                #     if person.destination_time == i:
                #         if isinstance(person, Employee):
                #             driver_arrivals[station][i - time] += 1
                #
                #         vehicle_arrivals[station][i - time] += 1
                #         break
                if person.destination_time == i:
                    if isinstance(person, Employee):
                        driver_arrivals[station][i - time] += 1
                    if person.vehicle_id is not None:
                        vehicle_arrivals[station][i - time] += 1
                else:
                    break

        ########################################
        # Fraction of Time for at Capacity or Empty ~ JS
        ########################################

        num_parked_cars = len(station_dict[station].car_list)
        num_park_spots = 50 - len(station_dict[station].car_list)

        if num_parked_cars == 0:
            total_time_empty[station] += 1

        if num_parked_cars == num_park_spots:
            total_time_full[station] += 1

    ######################################
    # Creating Forecast Dictionary ~ NM/MC
    ######################################
    if controller_type == 'smart':
        Forecast = {
            # 'demand' : demand_forecast_parser(time), # ~ MC
            'demand': demand_forecast_parser_alt(time),
            'vehicleArrivals': vehicle_arrivals,  # ~ NM
            'driverArrivals': driver_arrivals,  # ~ NM
        }

        # print("FORECAST")
        # for k, v in Forecast.items():
        #     print(k, v.shape)

        ######################################
        # Creating State Dictionary ~ JS
        ######################################

        State = {
            'idleVehicles': np.array(idle_vehicles),
            'idleDrivers': np.array(idle_drivers),
            'privateVehicles': np.zeros((58, 1))
        }

        # Fake data RoadNetwork
        # RoadNetwork = np.load("./roadNetwork.npy").item()

        # create controller if it doesn't already exist
        try:
            controller
        except:
            controller = MoDController(RoadNetwork)

        # Other Fake State data for testing.
        # Parameters = np.load("./parameters.npy").item()
        # State = np.load("./state.npy").item()
        # Forecast = np.load("./forecast.npy").item()
        # Flags = np.load("./flags.npy").item()

        [tasks, controller_output] = controller.computerebalancing(Parameters, State, Forecast, Flags)
        # for task in tasks:
        #     print(task)
        #
        # for c_output in controller_output:
        #     print(c_output)

    elif controller_type == 'naive':

        if morningStart <= time and time <= morningEnd:
            morning_rebalancing(station_dict)
            morningStart += 24
            morningEnd += 24
        elif eveningStart <= time and time <= eveningEnd:
            evening_rebalancing(station_dict)
            eveningStart += 24
            eveningEnd += 24

    print('\n\n*****************************\n\n')

    text_file_output.append('Errors: {}'.format(errors))

    pedestrian_requests = tasks['driverRebalancingQueue']
    # for request in pedestrian_requests:
    #     print(request)
    vehicle_requests = tasks['vehicleRebalancingQueue']
    print(pedestrian_requests)
    print(vehicle_requests)

    text_file_output.append('Errors: {}'.format(errors))

    # driver_requests = format_instructions(text_file_output_requests)
    # customer_requests = format_instructions(text_file_output_requests)

######################################
# Tracking Errors / Summing Errors ~ JS
######################################

sum_station_no_park_errors = np.sum(no_park_errors, axis=0)  # no parking errors per station total
sum_station_no_car_cust_errors = np.sum(no_car_cust_errors, axis=0)  # no car available for customers errors per station
sum_station_no_car_emp_errors = np.sum(no_car_emp_errors, axis=0)  # no car available for employees errors per station

sum_time_no_park_errors = np.sum(no_park_errors, axis=1)  # no parking errors per time total
sum_time_no_car_cust_errors = np.sum(no_car_cust_errors, axis=1)  # no car available for customers errors per time total
sum_time_no_car_emp_errors = np.sum(no_car_emp_errors, axis=1)  # no car available for employees errors per time total

######################################
# Writing to text_file_output File ~ NM
######################################

text_file_output_file = open('text_file_output.txt', 'w')

for item in text_file_output:
    text_file_output_file.write("%s\n" % item)

text_file_output_file.close()