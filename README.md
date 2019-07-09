# ASL-HA-MO-Simulator-Project

This project is a simulator for the HA:MO systems in Japan.
In this project, we utilize two different types of controllers:
- The Naive Controller: The status quo
- The Smart Controller: The challenger

By creating this simulator, we hope to gauge the effectiveness of the two controllers.


**Created by:**
 Nicholas Masri, Matt Cooley, and Jackson Schilling

**Project Mentor:** Matthew Tsao

**Sponsored By:** Marco Pavone: Autonomous Systems Lab, Stanford University




## User Guide

**Requirements**

OS Version: This project uses Python 3 for all code

Python Modules: Use `pip -r install requirements.txt` which can be found in the main directory. This requirements file includes all of the necessary packages for python that you will need to run the naive controller. However, if you want to run the smart controller, there is a requirements.txt file in that folder that will include the all of the necessary packages for the controller. You will also need to install MATLAB and CPLEX, and give the controller your file path to those in order to make it work in the controller/write_ups/hamod.py file held in the file_path variable.



**Setup**

Use the given controller examples (naive and optimal) or plug in your own controller into the controller folder. The controller will need to spit out specified instructions to the simulator, which will then give back the system state. The initialization and system parameters will need to be set in simulator/setup.py. Any data needed to pull from will need to be placed in the data folder, including numpy arrays and .csv files. 

**Running the simulator**

To run the simulator, run main.py, which will turn to run.py, which will prompt which controller you want to run the simulator with, being the naive controller, the optimal controller, or a controller of your own. This then plugs in that controller into the run.py loop, which will loop through the update.py function of the program using the setup.py and parameters.py variables. 

This loop will run the remainder of the runtime, recording data into the station_overview.txt and measurements.txt files, allowing for data review afterwards. Specify the location of this file if need be. 

All of the objects for the program are created from the station.py and people.py files, to keep track of each station state and employee state, respectively. helpers.py contains any methods used by the rest of the program that do not belong to a station or person class. Most of these methods are used in the update.py loop. 

**Output**

The output data will be located in the simulator/output folder, with the heatmap.py and measurement.py files. overview.py contains the text function for how the outputs are formatter. heatmap.py creates and saves heatmaps based on station states, but may have to be changed in some ways if a new controller is to be used with the simulator. measurement.py contains all of the methods to record and store the data from the program, including statistics from the station states and the errors they incur as the simulator runs. 

The output and measurement data will be stored in the files folder, with matplotlib visual data being stored under files/pictures, containing the error graphs over time, the heatmap visualizations over time, and the standard deviation data over time. The files folder also contains the measurements.txt and station_overview.txt files. 


**File Descriptions**

`run.py`

Contains the main run loop, which calls the cust_requests function to plug the result into the update class to be run. Also creates the station_overview.txt and measurements.txt files. For each loop run, the output is appended to the text files. This imports from update.py, simulator/setup.py, output/overview.py, and output/measurement.py

_`main.py`_

Contains the main function, which prompts the user for a controller selection, and initializes the controller accordingly. Imports simulator/run.py 

`parameters.py`

Contains the initialization for how many employees are placed at each station at the beginning of the simulation. It also lists the definitions of the data for station_data, parking_data, mean_data, and customer_data, which are all located in the data folder. Does not import any other modules. 

`setup.py`

Contains all of the program’s variable declarations, notably for plugging them into the controller being used. The stations .csv import time horizon, time step size, and modes of transport are the main things to consider if there is a need to change any of the variables given. Imports simulator/variables/parameters.py, simulator/variables/helpers.py, numpy, pandas, and datetime

`people.py`

Contains the initialization for each of the employee objects in the simulator and their internal methods. Imports simulator/setup.py

`stations.py`

Contains the initialization for each of the station objects in the simulator and their internal methods. Imports operator

`update.py`

Contains the update functions stored in update objects so that the variables given and used will be more self-contained. Includes the loop, arrivals, assign_drivers, reroute_for_overflow, assign_pedestrians, assign_customers, naive, smart, smart_setup, and station_initializer functions. Both the naive and smart_setup functions are used to setup controller types, and if a custom controller is used, we recommend setting it up by including your own function based on ours in this module. Imports simulator/output/overview.py, simulator/variables/parameters.py, simulator/people.py, and simulator/stations.py

`helpers.py`

Contains functions to “help” other modules, notably the update loop. Includes the format_instructions, format_travel_times, demand_forecast_parser, demand_forecast_formatter, fix_header, fix_row_headers, and parse_ttimes functions. Imports numpy and pandas 

`measurement.py`

Contains functions made to measure outputs and data gathered from the system states as the simulation progresses through simulated time. Inside the Measurement class, includes the measure_station and record functions. In addition, inside the record function, errors are recorded and written to a .txt file. Imports numpy, math, and matplotlib

`heatmap.py`

Contains the functions needed to run a heatmap file generator decoupled from the simulator after it has finished running, and save the files created to a folder in files/pictures/heatmaps with corresponding titles and filenames depending on the timestep they are generated from within the recorded simulator data. Includes own NaiveForecaster class, allowing it to get forecasted data live after the simulator has stopped running (may need to be tweaked if using another controller type), along with the score, degrees_to_pixels, and heatmap_run functions. Major changes will need to be made to the heatmap_run function if using your own controller, but only near the top-most code of the function. Imports pandas, numpy, matplotlib, and sys

`overview.py`

Contains the output and write functions, responsible for outputting stored data to .txt files to be read after the simulator is done fully running. The output function stores station indices, the number of idle_vehicles, the available parking, and the number of people en-route to that station for each station at each timestep the program is run for. Does not import any other modules.
