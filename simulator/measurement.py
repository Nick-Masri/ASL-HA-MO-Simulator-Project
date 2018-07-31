import numpy as np
from math import ceil

class Measurement:
    def __init__(self):
        self.park_errors = np.zeros([2880, 58]).astype(int)
        self.time_empty = np.zeros([58, 10]).astype(int)
        self.time_full = np.zeros([58,10]).astype(int)

    def measure(self, time, station, station_index):
        calc = station.get_en_route_drivers() - station.calc_parking()
        if station.parking_spots != 0:
            if calc > 0:
                self.park_errors[time][station_index] = calc

            day = ceil(time/288) - 1

            if station.calc_parking() == 0:
                self.time_empty[station_index][day] += 1

            if station.calc_parking() == station.parking_spots:
                self.time_full[station_index][day] += 1

    def record(self, file):
        errors = open(file, 'w')
        avg_time_full = np.mean(self.time_full / 2.88)
        avg_time_empty = np.mean(self.time_empty / 2.88)

        for day in range(10):
            errors.write("\n\nDay: {}\n".format(day+1))
            std_full = np.std(self.time_full[:][day], dtype=np.float64)
            std_empty = np.std(self.time_empty[:][day], dtype=np.float64)
            errors.write("Standard Deviation Full: {}\n".format(std_full))
            errors.write("Standard Deviation Empty: {}\n".format(std_empty))
            for i in range(58):
                errors.write("\n\n\tStation {}:\n".format(i))
                for x in range((day+1)*288):
                    if self.park_errors[x][i] != 0:
                        errors.write("\t\tAt time {0}, there were {1} cars that did not get parking\n".format(x,
                                                                        int(self.park_errors[x][i])))
                errors.write("\t\tThis station was full {} % of the time\n".format(self.time_full[i][day]/2.88))
                errors.write("\t\tThis station was empty {} % of the time\n".format(self.time_empty[i][day]/2.88))


        errors.write("Average Time Full: {}%\n".format(avg_time_full))
        errors.write("Average Time Empty: {}%\n".format(avg_time_empty))

        errors.close()