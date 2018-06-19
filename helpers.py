from classes import *

def checkEveryMinute():
    pass


def instructionsEveryHour():
    pass


def CreateDict(_list):
    _dict = {}
    for x in _list:
        _dict[x[0]] = Asset(x[0], x[1])
    return _dict

def calc_d_time(origin, destination, o_time):
    travel_time = graph[o][d]
    d_time = travel_time + o_time
    return d_time