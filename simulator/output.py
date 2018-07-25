def output(time, station_dict):
    text = []
    text.append("\nTime: {}".format(time))
    text.append('------------------------------------------------------')

    for station_index in sorted(station_dict):

        station = station_dict[station_index]
        text.append('\tStation: {}'.format(station_index))
        text.append('\t\tNumber of Idle Vehicles: {}'.format(len(station.car_list)))
        text.append('\t\tAvailable Parking: {}'.format(station.calc_parking()))
        text.append(
            '\t\tNum People En_Route: {}'.format(len(station.get_en_route_list())))

    # text.append('Errors: {}'.format(errors))

    return text


def write(file, text):
    output_file = open(file, 'w')
    for item in text:
        for x in item:
            output_file.write("%s\n" % x)

    output_file.close()
