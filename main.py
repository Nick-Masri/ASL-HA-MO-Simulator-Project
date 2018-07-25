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

