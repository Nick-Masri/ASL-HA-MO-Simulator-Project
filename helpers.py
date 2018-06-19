from classes import *

def checkEveryMinute():
    pass


def instructionsEveryHour():
    pass


def CreateDict(list):
    dict = {}
    for x in list:
        dict[x[0]] = Asset(x[0], x[1])
    return dict

def calc_d_time(origin, destination, o_time):
    travel_time = graph[o][d]
    d_time = travel_time + o_time
    return d_time