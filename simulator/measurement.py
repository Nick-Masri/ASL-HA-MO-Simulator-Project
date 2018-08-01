import numpy as np
from math import ceil


class Measurement:
    def __init__(self):
        self.park_errors = np.zeros([2880, 58]).astype(int)
        self.time_empty = np.zeros([58, 10]).astype(int)
        self.time_full = np.zeros([58,10]).astype(int)
        self.park_errors = 0
        self.vehicle_errors = 0

    def measure_station(self, time, station, station_index):
        calc = station.get_en_route_drivers() - station.calc_parking()
        if station.parking_spots != 0:

            day = ceil(time/288) - 1

            if station.calc_parking() == 0:
                self.time_full[station_index][day] += 1

            if station.calc_parking() == station.parking_spots:
                self.time_empty[station_index][day] += 1

    def record(self, file,):
        errors = open(file, 'w')

        for day in range(10):
            errors.write("\n\nDay: {}\n".format(day+1))
            for i in range(58):
                errors.write("\n\n\tStation {}:\n".format(i))
                errors.write("\t\tThis station was full {} % of the time\n".format(self.time_full[i][day]/2.88))
                errors.write("\t\tThis station was empty {} % of the time\n".format(self.time_empty[i][day]/2.88))

        errors.write("\n\nMeans and STD:\n")
        for i in range(58):
            avg_time_full = np.mean(self.time_full[i][:] / 2.88)
            avg_time_empty = np.mean(self.time_empty[i][:] / 2.88)
            std_full = np.std(self.time_full[i][:] / 2.88, dtype=np.float64)
            std_empty = np.std(self.time_empty[i][:] / 2.88, dtype=np.float64)
            errors.write("\tStation {}\n".format(i))
            errors.write("\t\tStandard Deviation Full: {}\n".format(std_full))
            errors.write("\t\tStandard Deviation Empty: {}\n".format(std_empty))
            errors.write("\t\tAverage Time Full: {}%\n".format(avg_time_full))
            errors.write("\t\tAverage Time Empty: {}%\n".format(avg_time_empty))

        errors.write("\n\nErrors:\n")
        errors.write("\tThere were {} times when a customer or employee did not get a car\n".format(self.vehicle_errors))
        errors.write("\tThere were {} times when a customer could not park\n".format(self.park_errors))

        errors.close()