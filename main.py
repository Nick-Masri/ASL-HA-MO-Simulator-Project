#!/usr/bin/python
from simulator.run import run


def main():
    print("What controller do you want to run?")
    controller_type = (input("N/Naive or S/Smart:\n")).lower()
    controller_types = ("n", "naive", "s", "smart")

    if controller_type in controller_types:
        run(controller_type)
    else:
        print("Not a Valid Input")
        main()


if __name__ == '__main__':
    main()