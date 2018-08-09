import pandas as pd
import numpy as np
import sys
import matplotlib.pyplot as plt

"""
Heatmap code takes inputs for station input_data, including longitude, latitude, available parking_per_station, idle vehicles, 
arrival demand, and departure demand per station. The program then performs a calculation based on this input_data to give 
each station a "score", which allows it to be placed and shown on a heatmap with other stations based on the condition
it is in and the need for rebalancing. The more highlighted it is, the worse of a condition it is in. Ideally, all
stations are a flat blue. It then either shows the heatmap file or saves it to a local folder, with the output_files being .png
and having dimensions of 640 x 480 pixels. 

INPUTS: 
- .csv file containing ordered information for each station, including
      longitude
      latitude
      available parking_per_station
      idle vehicles
      expected arrivals
      expected departures
  look at sample input_data given for structure needed

- time start (integer)

- (58,) ordered list of idle_vehicles

- (58,) ordered list of available_parking

All 3 inputs going into heatmap_run(current_time, idle_vehicles, available_parking)

RESULT:
- Saves heatmap output_files in output_files/heatmaps
"""

points = []
jst = np.load("input_data/10_days/time10days.npy")


class NaiveForecaster:
    def __init__(self, day_forecast_path, timestepsize, horizon, id_to_idx_path):
        forecaster = np.load(day_forecast_path)
        # ugly hack
        shape = forecaster.shape
        hacky_forecaster = np.zeros((shape[0] * 2, shape[1], shape[2]))
        hacky_forecaster[:shape[0], :, :] = forecaster
        hacky_forecaster[shape[0]:, :, :] = forecaster
        self.forecaster = hacky_forecaster
        # end hack
        self.timestepsize = timestepsize
        self.nsteps = (3600 * 24) / (timestepsize * 60)
        self.horizon = horizon
        self.id_to_idx = np.load(id_to_idx_path).item()
        return

    def predict(self, timestamp, station_ids):
        # print(self.id_to_idx.keys())
        # convert timestep into step
        # time_now = timestamp.time()
        # step = time_now.hour * 3600. + time_now.minute * 60. + time_now.second
        # step = int(np.round((step / self.timestepsize * 60)))
        step = timestamp
        # initialize forecast
        forecast = np.zeros((len(station_ids), len(station_ids), self.horizon))
        # find the idx
        f_index = []  # for which stations do we have a forecast
        new_index = []  # what is their equivalent in the estimator
        for i, station_id in enumerate(station_ids):
            if str(station_id) in self.id_to_idx.keys():
                f_index.append(i)
                new_index.append(self.id_to_idx[str(station_id)])
        f_idx = np.ix_(f_index, f_index)
        idx = np.ix_(new_index, new_index)
        # assign the forecast
        # I hope there was a faster way
        # q = self._get_min_q(self.forecaster, step)
        for i in range(self.horizon):
            # forecast[:, :, i][f_idx] = poisson.ppf(q,self.forecaster[step+i, :, :][idx])
            forecast[:, :, i][f_idx] = self.forecaster[step + i, :, :][idx]
        # print('Forecasted demand: {}'.format(forecast.sum()))
        return forecast


def score(expected_demand, idle_vehicles, expected_arrivals, available_parking):
    demand_out = expected_demand - idle_vehicles
    demand_in = expected_arrivals - available_parking

    if demand_out > demand_in:
        evaluation = 2 * demand_out
    else:
        evaluation = 2 * demand_in

    if evaluation >= 10:
        s = 10
    elif evaluation <= 0:
        s = 0
    else:
        s = evaluation

    return s


def degrees_to_pixels(long, lat, max_width, max_height, locations):
    rangelat = np.max(locations[:, 0]) - np.min(locations[:, 0])
    rangelong = np.max(locations[:, 1]) - np.min(locations[:, 1])

    width = max_width / rangelong
    length = max_height / rangelat

    x = width * (long - np.min(locations[:, 1]))
    y = length * (lat - np.min(locations[:, 0]))
    points.append([x, y])
    return np.array([x, y])


def heatmap(log, time):

    id_to_idx_path_map = './input_data/10_days/station_mapping.npy'
    forecast_path = './input_data/mean_demand_weekday_5min.npy'
    time_step_size = 5
    time_horizon = 12

    # initializes naive forecaster
    forecaster_obj = NaiveForecaster(forecast_path, time_step_size, time_horizon, id_to_idx_path_map)

    # grab station states for predict method
    stations = pd.read_csv('./input_data/stations_state_indexed.csv').set_index('station_id')
    station_ids = stations.index.tolist()
    # set time start for predict method

    start_time = time % 288

    forecast_prediction = forecaster_obj.predict(start_time, station_ids)
    demand_all = np.zeros([58, 58])
    for _ in range(0, 12):
        demand_all = demand_all + np.sum(forecast_prediction, axis=2)

    forecast_demand = np.sum(demand_all, axis=1)
    forecast_arrivals = np.sum(demand_all, axis=0)

    # image size settings
    imageWidth = 640
    imageHeight = 480

    locations = pd.read_csv('./input_data/stations_state.csv').loc[:, ['longitude', 'latitude']]
    env = np.zeros((len(locations), imageWidth, imageHeight))
    pix = np.zeros((imageWidth, imageHeight, 2))
    for j in range(imageWidth):
        for k in range(imageHeight):
            pix[j][k][1] = k
            pix[j][k][0] = j

    idle_vehicles = np.load('output_files/state_data/idle_vehicles.npy')[:, time]
    available_parking = np.load('output_files/state_data/available_parking.npy')[:, time]
    data = {'ed': forecast_demand, 'iv': idle_vehicles, 'ea': forecast_arrivals, 'ap': available_parking}

    for i in range(len(data)):

        s = score(data['ed'][i], data['iv'][i], data['ea'][i], data['ap'][i])
        coordinates = degrees_to_pixels(locations['longitude'].values[i], locations['latitude'].values[i], imageWidth, imageHeight, locations.values)
        env[i, :, :] = -.005 * ((pix[:, :, 0] - coordinates[0]) ** 2 + (pix[:, :, 1] - coordinates[1]) ** 2)
        env[i, :, :] = s * np.exp(env[i, :, :])

    grayscale = np.sum(env, axis=0)

    plt.imshow(grayscale.T, cmap='jet')
    plt.gca().invert_yaxis()

    locations = locations.values
    X = locations[:, 1] - np.min(locations[:, 1])
    X = imageWidth * X / np.max(X)
    Y = locations[:, 0] - np.min(locations[:, 0])
    Y = imageHeight * Y / np.max(Y)

    plt.scatter(X, Y, s=8, c='w', marker='.')
    # plt.show()

    plt.title('Time of Day: {}'.format(jst[time].time()))  # adds corresponding titles
    plt.savefig('output_files/graphs/heatmaps/heatmap_{}.png'.format(time), bbox_inches='tight')  # saves pics with diff names


def heatmap_run(log):

    for time in range((log['parking_violation']).shape[1]):
        if time % 6 == 0:
            heatmap(log, time)

    print("\noutput_files/graphs/heatmaps/* created")