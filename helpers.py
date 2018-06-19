from classes import *
# import __init__

def checkEveryMinute():
    ## Old lists
    # update arrivals status (if dt = curr)
    # update departures status (if ot = curr)

    ## New lists
    # update the status of new customers/ employees (everyone not in a list)
    # Figure out who we prioritize
    pass

def instructionsEveryHour():
    pass


def create_dict(_list):
    _dict = {}
    for x in _list:
        _dict[x[0]] = Asset(x[0], x[1])
    return _dict

# def calc_d_time(origin, destination, o_time):
#     return __init__.GRAPH[origin][destination] + o_time
