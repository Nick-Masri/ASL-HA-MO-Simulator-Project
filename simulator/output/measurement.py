import numpy as np
from math import ceil
import matplotlib.pyplot as plt

import pandas as pd



class Measurement:
    def __init__(self):
        self.park_errors = np.zeros([2880, 58]).astype(int)
        self.time_empty = np.zeros([58, 10]).astype(int)
        self.time_full = np.zeros([58,10]).astype(int)
        self.park_errors = np.zeros([58, 10]).astype(int)
        self.vehicle_errors = np.zeros([58, 10]).astype(int)
        # self.park_errors = 0
        # self.vehicle_errors = 0self.park_errors = 0
        # self.vehicle_errors = 0

    def measure_station(self, time, station, station_index):
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

        mapping = np.load("data/10_days/station_mapping.npy").item()
        station_ids = pd.read_csv('data/stations_state.csv')['station_id'].tolist()

        for day in range(5):
            x = np.array([i for i in range(58)])
            y = self.time_empty[:, day]
            e = []
            temp = []
            for station in station_ids:
                temp.append(y[mapping[str(station)]])
            for i in range(58):
                e.append(np.std(self.time_empty[i][:]/2.88))
            plt.ylim(0, 300)
            plt.xlim(0,58)
            plt.plot([0, 58], [np.mean(y), np.mean(y)], '--', c='r')
            plt.bar(x, temp)

            plt.title("Naive Controller: Time Empty Day {}".format(day+1))
            plt.savefig("files/pictures/STD/Time_Empty_Day: {}".format(day+1))
            plt.clf()

        for day in range(5):
            x = np.array([i for i in range(58)])
            y = self.time_full[:, day]
            e = []
            temp = []
            for station in station_ids:
                temp.append(y[mapping[str(station)]])
            for i in range(58):
                e.append(np.std(self.time_empty[i][:] / 2.88))
            plt.ylim(0, 300)
            plt.xlim(0, 58)
            plt.plot([0, 58], [np.mean(y), np.mean(y)], '--', c='r')
            plt.bar(x, temp)
            plt.title("Naive Controller: Time Full Day {}".format(day+1))
            plt.savefig("files/pictures/STD/Time_Full_Day: {}".format(day + 1))
            plt.clf()


        for day in range(5):
            x = np.array([i for i in range(58)])
            y = self.park_errors[:, day]
            e = []
            temp = []
            for station in station_ids:
                temp.append(y[mapping[str(station)]])
            for i in range(58):
                e.append(np.std(self.park_errors[i][:] / 2.88))
            plt.ylim(0, 10)
            plt.xlim(0, 58)
            plt.plot([0, 58], [np.mean(y), np.mean(y)], '--', c='r')
            plt.bar(x, temp)
            plt.title("Naive Controller: Park Errors Day: {}".format(day+1))
            plt.savefig("files/pictures/errors/Park_Errors_Day: {}".format(day + 1))
            plt.clf()

        for day in range(5):
            x = np.array([i for i in range(58)])
            y = self.vehicle_errors[:, day]
            e = []
            temp = []
            for station in station_ids:
                temp.append(y[mapping[str(station)]])
            for i in range(58):
                e.append(np.std(self.vehicle_errors[i][:] / 2.88))
            plt.ylim(0, 30)
            plt.xlim(0, 58)
            plt.plot([0, 58], [np.mean(y), np.mean(y)], '--', c='r')
            plt.bar(x, temp)
            plt.title("Naive Controller: Vehicle Errors Day: {}".format(day+1))
            plt.savefig("files/pictures/errors/Vehicle_Errors_Day: {}".format(day + 1))
            plt.clf()
        # sphinx_gallery_thumbnail_number = 2

        # stations = []
        # for i in mapping:
        #     stations.append(i)
        #
        # time = [i for i in range(5)]
        #
        # harvest = self.park_errors[0:5]
        #
        # fig, ax = plt.subplots()
        # im = ax.imshow(harvest)
        #
        # # We want to show all ticks...
        # ax.set_xticks(np.arange(len(time)))
        # ax.set_yticks(np.arange(len(stations)))
        # # ... and label them with the respective list entries
        # ax.set_xticklabels(time)
        # ax.set_yticklabels(stations)
        #
        # # Rotate the tick labels and set their alignment.
        # plt.setp(ax.get_xticklabels(), rotation=45, ha="right",
        #          rotation_mode="anchor")
        #
        # # Loop over data dimensions and create text annotations.
        # for i in range(len(stations)):
        #     for j in range(len(time)):
        #         text = ax.text(j, i, harvest[i, j],
        #                        ha="center", va="center", color="w")
        #
        # ax.set_title("Harvest of local farmers (in tons/year)")
        # fig.tight_layout()
        # plt.show()


        errors.write("\n\nErrors:\n")
        errors.write("\tThere were {} times when a customer or employee did not get a car\n".format(self.vehicle_errors))
        errors.write("\tThere were {} times when a customer could not park\n".format(self.park_errors))

        errors.close()