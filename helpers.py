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