def morning_rebalancing(dict):
    driver_task = [[] for i in range(58)]
    pedestrian_task = [[] for i in range(58)]
    home = (22, 55)
    buffer = (38, 41)
    extra = (37,43)
    for i in home:
        station = dict[i]
        for emp in station.employee_list:
            if len(station.car_list) > 0:
                for dest in buffer:
                    if dict[dest].calc_parking() > 0:
                        driver_task[i] = [dest]
                        break
                else:
                    for dest in extra:
                        if dict[dest].parking_spots > 0:
                            driver_task[i] = [dest]
                    else:
                        break

    for i in buffer + extra:
        if dict[home[0]].calc_parking() + dict[home[1]].calc_parking() == 0:
            break
        station = dict[i]
        if dict[home[0]].calc_parking() > dict[home[1]].calc_parking():
            dest = home[1]
        else:
            dest = home[0]

        for emp in station.employee_list:
            pedestrian_task[i] = [dest]
    # print(driver_task, pedestrian_task)
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
                for dest in buffer:
                    if dict[dest].calc_parking() > 0:
                        driver_task[i] = [dest]
                        break
            else:
                break

    for i in buffer:
        station = dict[i]
        if dict[home[0]].calc_parking() > dict[home[1]].calc_parking():
            dest = home[1]
        else:
            dest = home[0]

        for emp in station.employee_list:
            pedestrian_task[i] = [dest]
    # print(driver_task, pedestrian_task)
    return driver_task, pedestrian_task