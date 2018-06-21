GRAPH_VAR = [[0,5,8,11,13,13,12,11,8,5],  # needs to be 50x50 eventually
             [5,0,5,8,11,13,13,12,11,8],
             [8,5,0,5,8,11,13,13,12,11],
             [11,8,5,0,5,8,11,13,13,12],
             [12,11,8,5,0,5,8,11,13,13],
             [13,12,11,8,5,0,5,8,11,13],
             [13,13,12,11,8,5,0,5,8,11],
             [11,13,13,12,11,8,5,0,5,8],
             [8,11,13,13,12,11,8,5,0,5],
             [5,8,11,13,13,12,11,8,5,0]]


# Initializing Setup Variables (Random rn)
# [Employee ID #, Station ID #]
EMPLOYEE_LIST = [[1, 2],
                 [2, 5],
                 [3, 7],
                 [4, 10]]

# [Car ID #, Station ID #]
CAR_LIST = [[1, 1],
            [2, 2],
            [3, 2],
            [4, 4],
            [5, 4],
            [6, 6],
            [7, 9],
            [8,10]]


# Form of [origin][destination] = # of people requesting that route
PERSON_LIST = [[0,1,0],
               [2,0,3],
               [0,1,0]]

STATION_LIST = [num for num in range(11)]
