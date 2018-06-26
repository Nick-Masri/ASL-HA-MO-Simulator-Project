import pandas as pd
import numpy as np
from helpers import import_travel_times

import random
from itertools import repeat
random.seed(1477)

# Initializing the travel time matrices. They're Pandas DataFrames. Use the get method to get times.
CAR_TRAVEL_TIMES = import_travel_times("./data/travel_times_matrix_car.csv")
PEDESTRIAN_TRAVEL_TIMES = import_travel_times("./data/travel_times_matrix_walk.csv")
BIKE_TRAVEL_TIMES = import_travel_times("./data/travel_times_matrix_bike.csv")
HAMO_TRAVEL_TIMES = import_travel_times("./data/travel_times_matrix_hamo.csv")


####################
# INIT CONDITIONS #
##################

GRAPH_VAR = pd.read_csv('DATA/travel_times_matrix_hamo.csv')
GRAPH_VAR = GRAPH_VAR.set_index('station_id')
GRAPH_VAR.columns = pd.to_numeric(GRAPH_VAR.columns)
#print(GRAPH_VAR.index)
#print(GRAPH_VAR.loc[2549,30])
#print(GRAPH_VAR)

#################
# Instructions #
###############
