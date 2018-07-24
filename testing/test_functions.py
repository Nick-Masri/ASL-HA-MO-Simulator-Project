from helpers import *
from classes import *
from setup_vars import *

import numpy as np
import pandas as pd

car_travel_times = format_travel_times("./data/travel_times_matrix_car.csv", STATION_MAPPING, STATION_MAPPING_INT)
walking_travel_times = format_travel_times("./data/travel_times_matrix_walk.csv", STATION_MAPPING, STATION_MAPPING_INT)
hamo_travel_times = format_travel_times("./data/travel_times_matrix_hamo.csv", STATION_MAPPING, STATION_MAPPING_INT)


def test_get_travel_time():
    assert get_travel_time(hamo_travel_times, 53, 18) == 4

def test_demand_forecast_parser_right_length():
    assert len(demand_forecast_parser_alt(0)) == 58

def test_demand_forecast_formatter():
    demand = np.array([[[111,112],[121,122]],[[211,212],[221,222]],[[311,312],[321,322]]])
    predicted_formatted_demand = [[[111,211,311],[112,212,312]],[[121,221,321],[122,222,322]]]

    assert np.array_equal(demand_forecast_formatter(2, 3, demand), predicted_formatted_demand)





