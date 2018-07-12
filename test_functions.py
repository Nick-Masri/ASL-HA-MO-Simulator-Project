from helpers import *
from classes import *
import globals

import pandas as pd


def test_get_travel_time():
    assert get_travel_time(HAMO_TRAVEL_TIMES, 53, 18) == 4

def test_demand_forecast_parser_right_length():
    assert len(demand_forecast_parser(0, DEMAND_FORECAST)) == 12



