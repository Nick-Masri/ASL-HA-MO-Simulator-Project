##############################
# Naive Controller ~ NM
##############################


def morning_rebalancing(dict, ids):
    '''
    This code drives people from stations 22 and 55 to the
    stations in buffer/extra and then waks them back to whatever home
    station has the least amount of parking
    :param dict: The station dictionary to pull the station object
    :return: Returns the pedestrian task and driver task matrices
    '''
    driver_task = [[] for i in range(58)]
    pedestrian_task = [[] for i in range(58)]
    home = (22, 55)
    buffer = (38, 41)
    extra = (37,43)

    # Driving from home to buffer/extra
    for index, origin in enumerate(home):
        origin = dict[origin]

        for emp in origin.employee_list:
            if len(origin.car_list) > 0:
                for dest in buffer:
                    if dict[dest].calc_parking() > 1:
                        break
                else:
                    for dest in extra:
                        if dict[dest].calc_parking() > 1:
                            break
                    else:
                        break
                dest = dict[dest]
                driver_task[origin.station_id].append(dest.station_id)
            else:
                # If an employee at 22 or 55 has no car to drive, walk them to the other home station
                dest = dict[home[(index+1)%2]]
                if len(dest.car_list) > 0:
                    pedestrian_task[origin.station_id].append(dest.station_id)
                else:
                    break
    parking = []

    # Making the list of parking
    for dest in home:
        parking.append(dict[dest].calc_parking())

    # Walking the employees from buffer/extra to the home station with the least amount of parking
    ids = ids.copy()
    ids.remove(home[0])
    ids.remove(home[1])
    for origin in ids:
        origin = dict[origin]
        for emp in origin.employee_list:
            for i in range(len(parking)-1):
                if sorted(parking)[i] > 0:
                    dest = home[parking.index(sorted(parking)[i])]
                    break

            pedestrian_task[origin.station_id].append(dict[dest].station_id)
    return driver_task, pedestrian_task


def evening_rebalancing(dict, ids):
    '''
    Does the reverse of morning rebalancing
    :param dict:
    :return:
    '''
    driver_task = [[] for i in range(58)]
    pedestrian_task = [[] for i in range(58)]
    home = (38, 41, 37, 43)
    buffer = (22, 55)

    for index, origin in enumerate(home):
        origin = dict[origin]

        for emp in origin.employee_list:
            if len(origin.car_list) > 0:
                for dest in buffer:
                    if dict[dest].calc_parking() > 1:
                        break
                dest = dict[dest]
                driver_task[origin.station_id].append(dest.station_id)
            else:
                for i in range(4):
                    dest = dict[home[(index+i)%4]]
                    if len(dest.car_list) > 0:
                        pedestrian_task[origin.station_id].append(dest.station_id)
                    else:
                        break

    parking = []
    # Making the list of parking
    for dest in home:
        parking.append(dict[dest].calc_parking())

    # Walking the employees from buffer/extra to the home station with the least amount of parking

    ids = ids.copy()
    ids.remove(home[0])
    ids.remove(home[1])
    ids.remove(home[2])
    ids.remove(home[3])

    for origin in ids:
        origin = dict[origin]
        for emp in origin.employee_list:
            for i in range(len(parking)-1):
                if sorted(parking)[i] > 0:
                    dest = home[parking.index(sorted(parking)[i])]
                    pedestrian_task[origin.station_id].append(dict[dest].station_id)
                    break

    return driver_task, pedestrian_task