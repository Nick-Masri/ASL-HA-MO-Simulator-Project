import pandas as pd
import numpy as np


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
################