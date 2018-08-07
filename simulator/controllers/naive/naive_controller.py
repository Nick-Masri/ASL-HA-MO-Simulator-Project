##############################
# Naive Controller ~ NM
##############################


def morning_rebalancing(dict):
    driver_task = [[] for i in range(58)]
    pedestrian_task = [[] for i in range(58)]
    home = (22, 55)
    buffer = (38, 41)
    extra = (37,43)

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
                dest = dict[(index+1)%2]
                pedestrian_task[origin.station_id].append(dest.station_id)

    if dict[home[0]].calc_parking() != 0 and dict[home[1]].calc_parking() != 0:
        for origin in buffer + extra:
            origin = dict[origin]

            for emp in origin.employee_list:
                if dict[home[0]].calc_parking() > dict[home[1]].calc_parking():
                    dest = home[1]
                else:
                    dest = home[0]

                pedestrian_task[origin.station_id].append(dict[dest].station_id)
    print(driver_task, pedestrian_task)
    return driver_task, pedestrian_task


def evening_rebalancing(dict):
    driver_task = [[] for i in range(58)]
    pedestrian_task = [[] for i in range(58)]
    home = (38, 41, 37, 43)
    buffer = (22, 55)
    for i in home:
        station = dict[i]
        for emp in station.employee_list:
            if len(station.car_list) > 0:
                if dict[buffer[0]].calc_parking() > 0 and dict[buffer[0]].calc_parking() > 0:
                    if len(dict[buffer[0]].car_list) > len(dict[buffer[1]].car_list):
                        driver_task[i] = [buffer[1]]
                    else:
                        driver_task[i] = [buffer[0]]
                elif dict[buffer[0]].calc_parking() > 0:
                    driver_task[i] = [buffer[0]]
                elif dict[buffer[1]].calc_parking() > 0:
                    driver_task[i] = [buffer[0]]
            else:
                break

    for i in buffer:
        station = dict[i]
        if len(dict[home[0]].car_list) > 0 and len(dict[home[1]].car_list) > 0:
            if len(dict[home[0]].car_list) > len(dict[home[1]].car_list):
                dest = home[1]
            else:
                dest = home[0]
        elif len(dict[home[2]].car_list) > 0 and len(dict[home[3]].car_list) > 0:
            if len(dict[home[2]].car_list) > len(dict[home[3]].car_list):
                dest = home[3]
            else:
                dest = home[2]
        else:
            break
        for emp in station.employee_list:
            pedestrian_task[i] = [dest]
    # print(driver_task, pedestrian_task)
    return driver_task, pedestrian_task