import numpy as np


class Measurement:
    def __init__(self):
        self.park_errors = np.zeros([2880, 58])
        self.time_empty = np.zeros([58, 1])
        self.time_full = np.zeros([58,1])

    def measure(self, time, station, station_index):
        calc = len(station.get_en_route_list()) - station.calc_parking()
        if calc > 0:
            self.park_errors[time][station_index] = calc

        if station.calc_parking() == 0:
            self.time_empty[station_index] += 1

        if station.calc_parking() == station.parking_spots:
            self.time_full[station_index] += 1

    def record(self, file):
        errors = open(file, 'w')
        for i in range(58):
            errors.write("\n\nStation {}:\n".format(i))
            for x in range(2880):
                if self.park_errors[x][i] != 0:
                    errors.write("At time {0}, there were {1} cars that did not get parking\n".format(x,
                                                                    int(self.park_errors[x][i])))
            errors.write("This station was full for {} timesteps\n".format(int(self.time_full[i][0])))
            errors.write("This station was empty for {} timesteps\n".format(int(self.time_empty[i][0])))

        errors.close()