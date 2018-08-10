import numpy as np
import pandas as pd


def output(time, station_dict):
    text = []
    text.append("\nTime: {}".format(time))
    text.append('------------------------------------------------------')

    station_ids = pd.read_csv('input_data/stations_state.csv')['station_id'].tolist()
    
    for station in station_ids:

        station_obj = station_dict[station]
        text.append('\tStation: {}'.format(station))
        text.append('\t\tNumber of Idle Vehicles: {}'.format(len(station_obj.car_list)))
        text.append('\t\tAvailable Parking: {}'.format(station_obj.calc_parking()))
        text.append(
            '\t\tNumber of People En_Route: {}'.format(len(station_obj.get_en_route_list())))

    # text.append('Errors: {}'.format(errors))
    np.save('output_files/state_data/station_state', station_dict)
    return text


def write(file, text):
    output_file = open(file, 'w')
    for item in text:
        for x in item:
            output_file.write("%s\n" % x)
    print("\n\noutput_files/station_overview.txt created")
    output_file.close()
