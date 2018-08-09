import numpy as np
import matplotlib.pyplot as plt
import pandas as pd


class Measurement:

    def record(self, log, file):
        errors = open(file, 'w')

        for day in range(10):
            errors.write("\n\nDay: {}\n".format(day+1))
            for i in range(58):
                errors.write("\n\n\tStation {}:\n".format(i))
                errors.write("\t\tThis station was full {} % of the time\n".format(self.time_full[i][day]/2.88))
                errors.write("\t\tThis station was empty {} % of the time\n".format(self.time_empty[i][day]/2.88))

        errors.write("\n\nMeans and Full_Empty:\n")
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

        mapping = np.load("input_data/10_days/station_mapping.npy").item()
        station_ids = pd.read_csv('input_data/stations_state.csv')['station_id'].tolist()

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
            plt.savefig("output_files/graphs/Full_Empty/Time_Empty_Day: {}".format(day+1))
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
            plt.savefig("output_files/graphs/Full_Empty/Time_Full_Day: {}".format(day + 1))
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
            plt.savefig("output_files/graphs/errors/Park_Errors_Day: {}".format(day + 1))
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
            plt.savefig("output_files/graphs/errors/Vehicle_Errors_Day: {}".format(day + 1))
            plt.clf()

        errors.write("\n\nErrors:\n")
        errors.write("\tThere were {} times when a customer or employee did not get a car\n".format(self.vehicle_errors))
        errors.write("\tThere were {} times when a customer could not park\n".format(self.park_errors))

        print("\noutput_files/measurements.txt created")
        print("\noutput_files/graphs/errors/* created")
        print("\noutput_files/graphs/Full_Empty/* created")
        errors.close()