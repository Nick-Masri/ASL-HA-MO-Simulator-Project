from classes import *


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


def CreateDict(list):
    dict = {}
    for x in list:
        dict[x[0]] = Asset(x[0], x[1])
    return dict