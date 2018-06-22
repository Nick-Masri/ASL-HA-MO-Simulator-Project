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
EMPLOYEE_LIST = [[1, 5],
                 [2, 12],
                 [3, 36],
                 [4, 47]]

# [Car ID #, Station ID #], contains cars with unique IDs 
# (250 total, 0-249) assigned 5 to each station (50 total, 0-49)
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
PERSON_LIST = [[0,1,0],
               [2,0,3],
               [0,1,0]]

#STATION_LIST contains 51 stations, starting at 0, going to 50
STATION_LIST = [num for num in range(51)]
