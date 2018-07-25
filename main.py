#!/usr/bin/python
import simulator.run


def main():
    print("What controller do you want to run?")
    controller_type = input("N/Naive or S/Smart:\n")
    controller_types = ("N", "Naive", "S", "Smart")

    if controller_type in controller_types:
        simulator.run(controller_type)
    else:
        print("Not a Valid Input")
        main()

if __name__ == '__main__':
    main()



######################################
# Main Loop ~ NM
######################################
#
#
# raw_requests = np.load('./data/10_days/hamo10days.npy')
# cust_requests = format_instructions(raw_requests)
# driver_requests = [[] for i in range(len(station_dict))]
# pedestrian_requests = [[] for i in range(len(station_dict))]
#

#
# ######################################
# # Tracking Errors / Summing Errors ~ JS
# ######################################
#
# sum_station_no_park_errors = np.sum(no_park_errors, axis=0)  # no parking errors per station total
# sum_station_no_car_cust_errors = np.sum(no_car_cust_errors, axis=0)  # no car available for customers errors per station
# sum_station_no_car_emp_errors = np.sum(no_car_emp_errors, axis=0)  # no car available for employees errors per station
#
# sum_time_no_park_errors = np.sum(no_park_errors, axis=1)  # no parking errors per time total
# sum_time_no_car_cust_errors = np.sum(no_car_cust_errors, axis=1)  # no car available for customers errors per time total
# sum_time_no_car_emp_errors = np.sum(no_car_emp_errors, axis=1)  # no car available for employees errors per time total
#
# ######################################
# # Writing to text_file_output File ~ NM
# ######################################
#
# text_file_output_file = open('text_file_output.txt', 'w')
#
# for item in text_file_output:
#     text_file_output_file.write("%s\n" % item)
#
# text_file_output_file.close()