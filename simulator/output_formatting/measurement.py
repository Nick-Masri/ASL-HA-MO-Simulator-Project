import numpy as np
import matplotlib.pyplot as plt
import pandas as pd


class Measurement:

    def record(self, log, file):
        time_full = log['station_full']
        time_empty = log['station_empty']
        park_errors = log['parking_violation']
        vehicle_errors = log['no_vehicle_for_customer']

        errors = open(file, 'w')

        for day in range(10):
            errors.write("\n\nDay: {}\n".format(day+1))
            for i in range(58):
                errors.write("\n\n\tStation {}:\n".format(i))
                errors.write("\t\tThis station was full {} % of the time\n".format(time_full[i][day*288:(day+1)*288]/2.88))
                errors.write("\t\tThis station was empty {} % of the time\n".format(time_empty[i][day*288:(day+1)*288]/2.88))

        errors.write("\n\nMeans and Full_Empty:\n")
        for i in range(58):
            avg_time_full = np.mean(time_full[i][:] / 2.88)
            avg_time_empty = np.mean(time_empty[i][:] / 2.88)
            std_full = np.std(time_full[i][:] / 2.88, dtype=np.float64)
            std_empty = np.std(time_empty[i][:] / 2.88, dtype=np.float64)


            errors.write("\tStation {}\n".format(i))
            errors.write("\t\tStandard Deviation Full: {}\n".format(std_full))
            errors.write("\t\tStandard Deviation Empty: {}\n".format(std_empty))
            errors.write("\t\tAverage Time Full: {}%\n".format(avg_time_full))
            errors.write("\t\tAverage Time Empty: {}%\n".format(avg_time_empty))

        mapping = np.load("input_data/10_days/station_mapping.npy").item()
        station_ids = pd.read_csv('input_data/stations_state.csv')['station_id'].tolist()

        for day in range(10):
            x = np.array([i for i in range(58)])
            y = time_empty[:, day*288:(day+1)*288]
            y = np.sum(y, axis=0)
            e = []
            temp = []
            for station in station_ids:
                temp.append(y[mapping[str(station)]])
            # Standard Deviation Bars (For the future maybe)
            # for i in range(58):
            #     e.append(np.std(time_empty[i][:]/2.88))
            plt.ylim(0, 300)
            plt.xlim(0,58)
            plt.plot([0, 58], [np.mean(y), np.mean(y)], '--', c='r')
            plt.bar(x, temp)

            plt.title("Naive Controller: Time Empty Day {}".format(day+1))
            plt.savefig("output_files/graphs/Full_Empty/Time_Empty_Day: {}".format(day+1))
            plt.clf()

        for day in range(10):
            x = np.array([i for i in range(58)])
            y = time_full[:, day*288:(day+1)*288]
            y = np.sum(y, axis=0)
            e = []
            temp = []
            for station in station_ids:
                temp.append(y[mapping[str(station)]])
            # Standard Deviation Bars (For the future maybe)
            # for i in range(58):
            #     e.append(np.std(time_empty[i][:] / 2.88))
            plt.ylim(0, 300)
            plt.xlim(0, 58)
            plt.plot([0, 58], [np.mean(y), np.mean(y)], '--', c='r')
            plt.bar(x, temp)
            plt.title("Naive Controller: Time Full Day {}".format(day+1))
            plt.savefig("output_files/graphs/Full_Empty/Time_Full_Day: {}".format(day + 1))
            plt.clf()

        for day in range(10):
            x = np.array([i for i in range(58)])
            y = park_errors[:, day*288:(day+1)*288]
            y = np.sum(y, axis=0)
            e = []
            temp = []
            for station in station_ids:
                temp.append(y[mapping[str(station)]])
            # Error Bars (for the future maybe)
            # for i in range(58):
            #     e.append(np.std(park_errors[i][:] / 2.88))
            plt.ylim(0, 10)
            plt.xlim(0, 58)
            plt.plot([0, 58], [np.mean(y), np.mean(y)], '--', c='r')
            plt.bar(x, temp)
            plt.title("Naive Controller: Park Errors Day: {}".format(day+1))
            plt.savefig("output_files/graphs/errors/Park_Errors_Day: {}".format(day + 1))
            plt.clf()

        for day in range(10):
            x = np.array([i for i in range(58)])
            y = vehicle_errors[:, day*288:(day+1)*288]
            y = np.sum(y, axis=0)
            e = []
            temp = []
            for station in station_ids:
                temp.append(y[mapping[str(station)]])
            # Error Bars (for the future maybe)
            # for i in range(58):
            #     e.append(np.std(park_errors[i][:] / 2.88))
            plt.ylim(0, 30)
            plt.xlim(0, 58)
            plt.plot([0, 58], [np.mean(y), np.mean(y)], '--', c='r')
            plt.bar(x, temp)
            plt.title("Naive Controller: Vehicle Errors Day: {}".format(day+1))
            plt.savefig("output_files/graphs/errors/Vehicle_Errors_Day: {}".format(day + 1))
            plt.clf()

        errors.write("\n\nErrors:\n")
        errors.write("\tThere were {} times when a customer or employee did not get a car\n".format(np.sum(vehicle_errors)))
        errors.write("\tThere were {} times when a customer could not park\n".format(np.sum(park_errors)))

        print("\noutput_files/measurements.txt created")
        print("\noutput_files/graphs/errors/* created")
        print("\noutput_files/graphs/Full_Empty/* created")
        errors.close()