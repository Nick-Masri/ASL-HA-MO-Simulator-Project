import pandas as pd
import numpy as np
# from amod_forecasting import MultiStepLSTM
from .optimal_mod.modcontroller import MoDController
import copy
from scipy.stats import poisson


class NaiveForecaster:
    def __init__(self, day_forecast_path, timestepsize, horizon, id_to_idx_path):
        forecaster = np.load(day_forecast_path)
        # ugly hack
        shape = forecaster.shape
        hacky_forecaster = np.zeros((shape[0]*2, shape[1], shape[2]))
        hacky_forecaster[:shape[0], :, :] = forecaster
        hacky_forecaster[shape[0]:, :, :] = forecaster
        self.forecaster =hacky_forecaster
        # end hack
        self.timestepsize = timestepsize
        self.nsteps = 3600 * 24 / timestepsize.seconds
        self.horizon = horizon
        self.id_to_idx = np.load(id_to_idx_path).item()
        return 
    def predict(self, timestamp, station_ids):
        # convert timestep intio step
        # I removed the timestep to step. Already done.
        # time_now = timestamp.time()
        # step = time_now.hour * 3600. + time_now.minute * 60. + time_now.second
        # step = int(np.round((step/self.timestepsize.seconds)))
        step = timestamp % 288  # Added to handle multiple days (self.forecaster only has two days worth of data

        # initialize forecast
        forecast = np.zeros((len(station_ids),len(station_ids),self.horizon))
        print("Forecast Shape: {}".format(forecast.shape))
        # find the idx
        f_index = [] # for which stations do we have a forecast
        new_index = [] # what is their equivalent in the estimator
        for i,station_id in enumerate(station_ids):
            if str(station_id) in list(self.id_to_idx.keys()):  # if station ID is in the station_map keys
                f_index.append(i)  # Append the index of the key in the station_id list
                new_index.append(self.id_to_idx[str(station_id)])  # Append the logical index from the station_map in the same order as the station_ids list
        f_idx = np.ix_(f_index, f_index)  #
        idx = np.ix_(new_index, new_index)

        # assign the forecast
        # I hope there was a faster way
        #q = self._get_min_q(self.forecaster, step)
        for i in range(self.horizon):
            #forecast[:,:,i][f_idx] = poisson.ppf(
            #    q, 
            #    self.forecaster[step+i, :, :][idx]
            #    )
            forecast[:,:,i][f_idx] = self.forecaster[step+i, :, :][idx]  # forecast 0-57 is in the same order as the stationIDs
        print('Forecasted demand: {}'.format(forecast.sum()))
        return forecast

    def _get_min_q(self, mean_estimator, t):
        tot_diffs = []
        quants = np.arange(0.5, 0.99, 0.01)
        for q in quants:
            d = poisson.ppf(q, mean_estimator[t:t+self.horizon])
            diff = d.sum() - mean_estimator[t:t+self.horizon].sum()
            tot_diffs.append(np.abs(diff))
        return quants[np.argmin(tot_diffs)]


class Controller:

    def __init__(self, forecast_settings, control_settings):
        # one day
        # self.forecaster = MultiStepLSTM(**forecast_settings)
        # self.forecaster.set_params(forecast_settings['model_path'])
        # naive forecaster
        self.state = {}
        self.forecast = {}
        self.flags = {}
        self.flags['debugFlag'] = 0.
        self.flags['glpkFlag'] = 0.
        self.forecaster = NaiveForecaster(**forecast_settings)
        road_network = control_settings.pop('RoadNetwork')
        # I want a copy
        for key, value in road_network.items():
            setattr(self, key, copy.deepcopy(value))
        self.controller = MoDController(road_network)
        assert 'station_ids' in list(control_settings.keys())
        for key, value in control_settings.items():
            setattr(self, key, value)
        print("inside the controller")
        print(self.station_ids)
        return


    def set_state(self, stations_state):
        self.state['idleVehicles'] = stations_state.loc[self.station_ids]['idle_vehicles'].values
        self.state['idleDrivers'] = stations_state.loc[self.station_ids]['rebalancers'].values
        self.state['privateVehicles'] = stations_state.loc[self.station_ids]['private_vehicles'].values
        return

    def set_arrivals(self, ongoing_trips, current_time):
        ongoing_trips['ETA'] = pd.to_datetime(ongoing_trips['ETA']).dt.tz_localize('UTC').dt.tz_convert(self.timezone_name)
        ongoing_trips['eta_step'] = np.ceil((ongoing_trips['ETA'] - current_time).dt.seconds / self.horizon.seconds).astype(int) 
        N = len(self.station_ids)
        vehicleArrivals = pd.DataFrame(index = self.station_ids, columns = list(range(self.thor))).fillna(0)
        driverArrivals = pd.DataFrame(index = self.station_ids, columns = list(range(self.thor))).fillna(0)
        for trip in ongoing_trips.to_dict(orient = 'records'):
            dst = int(trip['station_id_dst'])
            assert dst in self.station_ids, "destination not in stations: {}".format(dst)
            eta = int(trip['eta_step'])
            if eta >= self.thor: continue
            try:
                vehicleArrivals.loc[dst][eta] = vehicleArrivals.loc[dst][eta] + 1
            except Exception as e:
                raise Exception("{}, {}, \n".format(dst, eta) + str(self.station_ids))
            if trip['is_rebalancing_trip']:
                driverArrivals.loc[dst][eta] = driverArrivals.loc[dst][eta] + 1
        self.forecast['vehicleArrivals'] = vehicleArrivals.values
        print(self.forecast['vehicleArrivals'])
        self.forecast['driverArrivals'] = driverArrivals.values
        return

    def update_state_arrivals(self, forecast, state):
        self.forecast['vehicleArrivals'] = forecast['vehicleArrivals']
        self.forecast['driverArrivals'] = forecast['driverArrivals']

        self.state['idleVehicles'] = state['idleVehicles']
        self.state['idleDrivers'] = state['idleDrivers']
        self.state['privateVehicles'] = state['privateVehicles']


    def forecast_demand(self, timestamp):
        future_demand = self.forecaster.predict(timestamp, self.station_ids)
        self.forecast['demand'] = future_demand
        return future_demand

    def compute_rebalancing(self):
        #TODO
        # check everything makes sense
        nroad = len(self.controller.RoadNetwork['roadGraph'])
        ntt = len(self.controller.RoadNetwork['travelTimes'])
        assert nroad == ntt,\
         "Number of stations mismatch: {} stations in the roadGraph, {} in the travel time matrix".format(nroad, ntt)
        if not self.thor >= self.forecaster.horizon:
            "[WARN] Horizon mismatch: {} in controller, {} in forecaster".format(
                self.thor, self.forecaster.horizon
                )
        assert self.forecast['demand'].shape[-1] == self.forecaster.horizon, \
         "Forecast length does not match expected horizon: {} in forecast, {} expected".format(
            self.forecast['demand'].shape[0],self.forecaster.horizon)
        # check parking constraints are not initially violated
        # parking - idle - arrivals > 0
        parking = self.parking
        idle = self.state['idleVehicles']
        arrivals = self.forecast['vehicleArrivals'].sum(axis=1)
        diff = parking - idle - arrivals
        mindx = np.argmin(diff) #
        assert np.max(diff) > 0, \
         "Parking constraints violated!Station {}: {} parking spots, {} idle, {} arriving".format(
            self.station_ids[mindx], parking[mindx],idle[mindx],arrivals[mindx])
        [tasks, paths] = self.controller.computerebalancing(self.params, self.state, self.forecast, self.flags)
        return tasks, paths
