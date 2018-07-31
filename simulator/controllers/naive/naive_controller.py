##############################
# Naive Controller ~ NM
##############################

def morning_rebalancing(dict):
    driver_task = [[] for i in range(58)]
    pedestrian_task = [[] for i in range(58)]
    home = (2, 5) # real station 22 = 2, 55 = 5
    buffer = (11, 37)# real station 38 = 11, 41=37
    extra = (27,10) # real station 37 = 27, 43 =10
    for i in home:
        station = dict[i]
        for emp in station.employee_list:
            if len(station.car_list) > 0:
                for dest in buffer:
                    if dict[dest].calc_parking() > 1:
                        driver_task[i] = [dest]
                        break
                else:
                    for dest in extra:
                        if dict[dest].calc_parking() > 1:
                            driver_task[i] = [dest]
                    else:
                        break

    for i in buffer + extra:
        if dict[home[0]].calc_parking() == 0 and dict[home[1]].calc_parking() == 0:
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
    home = (11, 37, 27, 10)
    buffer = (2, 5)
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
        if len(dict[home[0]].car_list) > 0 and len(dict[home[1]].car_list) > 0:
            if len(dict[home[0]].car_list) > len(dict[home[1]].car_list):
                dest = home[1]
            else:
                dest = home[0]
        elif len(dict[home[2]].car_list) > 0 and  len(dict[home[3]].car_list) > 0:
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