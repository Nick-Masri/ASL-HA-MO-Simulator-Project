from classes import *
from globals import *

def checkEveryMinute(station_dict):
    for station in station_dict:
        pass # loop one
        pass # loop four

def instructionsEveryHour():
    pass

def create_dict(_list):
    _dict = {}
    for x in _list:
        _dict[x[0]] = Asset(x[0], x[1])
    return _dict

def calc_d_time(origin, destination, o_time):
    return globals.GRAPH_var[origin][destination] + o_time
