def output(time, station_dict):
    text = []
    text.append("\nTime: {}".format(time))
    text.append('------------------------------------------------------')

    for station in sorted(station_dict):

        text.append('\tStation: {}'.format(station))
        text.append('\t\tNumber of Idle Vehicles: {}'.format(len(station_dict[station].car_list)))
        text.append('\t\tAvailable Parking: {}'.format(station.available_parking))
        text.append(
            '\t\tNum People En_Route: {}'.format(len(station_dict[station].get_en_route_list())))

    # text.append('Errors: {}'.format(errors))

    return text


def write(file, text):
    output_file = open(file, 'w')

    for item in text:
        output_file.write("%s\n" % item)

    output_file.close()
