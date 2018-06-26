import pandas as pd

import random
from itertools import repeat
random.seed(1477)

def import_travel_times(filename):
    return pd.read_csv(filename)


# hp.print_a_thing("This is a thing")

# Initializing the travel time matrices. They're Pandas DataFrames. Use the get method to get times.
CAR_TRAVEL_TIMES = import_travel_times("./data/travel_times_matrix_car.csv")
PEDESTRIAN_TRAVEL_TIMES = import_travel_times("./data/travel_times_matrix_walk.csv")
BIKE_TRAVEL_TIMES = import_travel_times("./data/travel_times_matrix_bike.csv")
HAMO_TRAVEL_TIMES = import_travel_times("./data/travel_times_matrix_hamo.csv")

# Station List
STATION_LIST = pd.to_numeric(CAR_TRAVEL_TIMES.columns.values[1:]).tolist()
print(STATION_LIST)

"""Initializing Setup Variables (Random rn)"""
# [Employee ID#, Station ID#]
EMPLOYEE_LIST = [[1, 5],
                 [2, 12],
                 [3, 36],
                 [4, 47]]

# [Car ID#, Station ID#]
# contains cars with unique IDs (250 total, ID# 0-249)
#   assigned 5 to each station ID (50 total, ID# 0-49)
CAR_LIST = []
temp_limit = 5
station_temp_id = 0
car_temp_id = 0
while car_temp_id <= temp_limit:
    CAR_LIST.append([car_temp_id, station_temp_id])
    car_temp_id = car_temp_id + 1
    if car_temp_id == 250:
        break
    if car_temp_id % 5 == 0:
        station_temp_id = station_temp_id + 1
        temp_limit = temp_limit + 5
    
#print(CAR_LIST)
#print(len(CAR_LIST))


# Form of [origin][destination] = # of people requesting that route
#PERSON_LIST = [[0,1,0],
#               [2,0,3],
#               [0,1,0]]

PERSON_LIST = [50*[0] for i in repeat(None, 50)]
for row in PERSON_LIST:
    for column in row:
        if column:
            pass 
        """UNIFINISHED"""
#print(PERSON_LIST)

#STATION_LIST contains 50 stations, starting at 0, going to 50
STATION_LIST = [num for num in range(50)]

#print(len(STATION_LIST))











