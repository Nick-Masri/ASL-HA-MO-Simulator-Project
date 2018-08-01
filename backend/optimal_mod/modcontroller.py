import numpy as np
import scipy.io as sio
from IPython import embed
import os
import time

# MATLAB stuff
import matlab.engine

class MoDController():
    '''

    NOTATION:
        N is the number of stations.
    
    INPUT FORMAT:
    'RoadNetwork' is a dictionary with the following fields:
        roadGraph (<N> list)
            A length N list containing numpy arrays.
            The ith array in the list is the set of neighbors of node i.
        travelTimes (<NxN> numpy array)
            A numpy array specifying how long it takes for a rebalancing ha:mo
            to travel between any pair of nodes.
        driverTravelTimes (<NxN> numpy array)
            A numpy array specifying how long it takes for a rebalancer
            to walk/bike between any pair of nodes.
        pvTravelTimes (<NxN> numpy array)
            A numpy array specifying the average time it takes for the private
            vehicle to travel between any pair of nodes.
        cTravelTimes (<NxN> numpy array)
            A numpy array where the (i,j) entry specifies the average amount of time
            a customer will spend with a vehicle that is picked up from station
            i and will be returned at station j.
        parking (<Nx1> numpy array)
            Specifies the total number of parking spots at each station.

    'Parameters' is a dictionary with the following fields:
        pvCap (int)
            Specifies the maximum number of rebalancers a private vehicle can carry
        driverRebalancingCost (float)
            Specifies the cost per distance of having a rebalancer walk/bike.
        vehiclerebalancingCost (float)
            Specifies the cost per distance of having a rebalancer drive a ha:mo.
        pvRebalancingCost (float)
            Specifies the cost per distance of having the private vehicle move.
        lostDemandCost (float)
            Specifies the cost incurred when a customer cannot find a nearby vehicle
            and leaves the system.
        thor (int)
            The planning horizon in multiples of 5 minutes.

    'State' is a dictionary with the following fields:
        idleVehicles (<Nx1> numpy array)
            Specifies the number of vehicles ready for customer use at each station
            at the beginning of the planning horizon.
        idleDrivers (<Nx1> numpy array)
            Specifies the number of rebalancers that do not currently have a task
            at each station at the beginning of the planning horizon.
        privateVehciles (int)
            Sspecifies the number of private vehicles at each station.

    'Forecast' is a dictionary with the following fields:
        demand (<NxNxT> numpy array)
            The (i,j,t) entry specifies the predicted number of customers who will
            request to pick up a ha:mo at station i at time t, which will be returned
            to station j.
        vehicleArrivals (<NxT> numpy array)
            The (i,t) entry specifies the number of previously occupied ha:mo vehicles
            that will become available at station i at time t.
        driverArrivals (<NxT> numpy array)
            The (i,t) entry specifies the number of previously busy rebalancers
            that will become available at station i at time t.

    'Flags' is a dictionary with the following fields:
        debugFlag (Bool)
            It was in the MATLAB version. I think it prints the status of the optimizer
        glpkFlag (Bool)
            Specify using glpk (True) or cplex (False)
    '''
    def __init__(self, RoadNetwork):
        print('starting matlab engine')
        t1 = time.time()
        start_eng = matlab.engine.start_matlab(async = True)
        while not start_eng.done():
            print('Waiting on start matlab engine')
            print('{} seconds elapsed.'.format(round(time.time() - t1)))
            time.sleep(5)
        self.eng = start_eng.result()
        print('matlab started')
        # This is the path to cplex on Matt's computer. On a different machine this will need to change.
        # self.eng.addpath('/opt/ibm/ILOG/CPLEX_Studio128/cplex/matlab/x86-64_linux')
        # self.eng.addpath(os.getenv('MATLAB_CPLEX_PATH'))
        file_path = '/Applications/CPLEX_Studio128/cplex/matlab/x86-64_osx'
        self.eng.addpath(file_path)
        # assumes this is being booted from the backend folder
        # Cooley Added
        self.eng.addpath('backend')
        self.eng.addpath(os.path.dirname(os.path.realpath(__file__)))
        # and if the env variable is set, it will check into the fullpath
        mod_path = os.getenv('OPT_MOD_PATH')
        # if mod_path:
        #     print('Loading mod path from env')
        #     self.eng.addpath(mod_path)
        MyOptions=self.eng.cplexoptimset('cplex');

        # convert roadgraph to matlab arrays
        for i in range(len(RoadNetwork['roadGraph'])):
            RoadNetwork['roadGraph'][i] = self.convert(RoadNetwork['roadGraph'][i])

        # convert parking capacities and travel times to matlab arrays.
        RoadNetwork['parking'] = self.convert(RoadNetwork['parking'])
        RoadNetwork['travelTimes'] = self.convert(RoadNetwork['travelTimes'])
        RoadNetwork['driverTravelTimes'] = self.convert(RoadNetwork['driverTravelTimes'])
        RoadNetwork['pvTravelTimes'] = self.convert(RoadNetwork['pvTravelTimes'])
        RoadNetwork['cTravelTimes'] = self.convert(RoadNetwork['cTravelTimes'])

        self.RoadNetwork = RoadNetwork

    def convert(self,A):
        # this function converts numpy arrays to matlab arrays.
        if type(A) is list:
            return matlab.double(A)
        return matlab.double(A.tolist())

    def format_inputs(self, State, Forecast):

        State['idleVehicles'] = self.convert(State['idleVehicles'])
        State['idleDrivers'] = self.convert(State['idleDrivers'])
        State['privateVehicles'] = self.convert(State['privateVehicles'])

        Forecast['demand'] = self.convert(Forecast['demand'])
        Forecast['vehicleArrivals'] = self.convert(Forecast['vehicleArrivals'])
        Forecast['driverArrivals'] = self.convert(Forecast['driverArrivals'])

        return State, Forecast

    def computerebalancing(self, Parameters, State, Forecast, Flags):
        State, Forecast = self.format_inputs(State, Forecast)
        t1 = time.time()
        hamod_task = self.eng.hamod(
            self.RoadNetwork,
            Parameters,
            State,
            Forecast,
            Flags, 
            nargout = 2, async = True,
            );
        while not hamod_task.done():
            print('Waiting on computation')
            print('{} seconds elapsed.'.format(round(time.time() - t1)))
            time.sleep(5)
        [tasks, output] = hamod_task.result()
        cleanpaths = []
        # modes = [
        #     "vehicleRebalancing",
        #     "driverRebalancing",
        #     "driverPassengerRebalancing",
        #     "privateVehicleRebalancing",
        # ]
        # cleanpath = []
        # for path in paths:
        #     try:
        #         cleanpath = [
        #                 [int(x - 1) for x in leg[0]] for leg in path
        #             ]
        #
        #
        #         for i in range(len(cleanpath)):
        #             cleanpath[i][-1] = modes[cleanpath[i][-1]] # matlab is 1-index
        #     except:
        #         print(path)
        #
        #     cleanpaths.append(cleanpath)

        return tasks, output
        # return tasks

def test():
    # set up some tests
    N = 30 # number of stations
    T = 10 # time horizon
    v = 100 # number of vehicles
    d = 2 # number of rebalancers
    lam = 1/float(N)

    print('Setting up RoadNetwork...')
    RoadNetwork = {}
    RoadNetwork['travelTimes'] = np.ones((N,N))
    RoadNetwork['pvTravelTimes'] = np.ones((N,N))
    RoadNetwork['cTravelTimes'] = np.ones((N,N))
    RoadNetwork['driverTravelTimes'] = 2*np.ones((N,N))
    np.fill_diagonal(RoadNetwork['driverTravelTimes'], 1)
    RoadNetwork['parking'] = (np.ceil(v/N) + 10)*np.ones((N,))

    RoadNetwork['roadGraph'] = []
    neighs = np.asarray(list(range(1,N+1))).reshape((1,N)) # REMEMBER! Matlab is 1 indexed.
    for i in range(N):
        RoadNetwork['roadGraph'].append(neighs)

    print('Setting Parameters...')
    Parameters = {}
    Parameters['pvCap'] = 4.
    Parameters['driverRebalancingCost'] = 1.
    Parameters['vehicleRebalancingCost'] = 1.
    Parameters['pvRebalancingCost'] = 1.
    Parameters['lostDemandCost'] = 1000.
    Parameters['thor'] = float(T)

    print('Setting State...')
    p = (1/float(N))*np.ones((N,)) # disperse cars and rebalancers uniformly.
    State = {}
    State['idleVehicles'] = np.random.multinomial(v, p)
    State['idleDrivers'] = np.random.multinomial(d, p)
    State['privateVehicles'] = np.zeros((N,1))
    #State['privateVehicles'][np.random.randint(0,N)] = 1

    print('Setting Forecast...')
    Forecast = {}
    Tinit = int(np.ceil(T))
    Forecast['demand'] = np.zeros((N,N,T))
    Forecast['demand'][:,:,0:Tinit] = lam#np.random.poisson(lam, (N,N,Tinit))
    # Forecast['demand'] = np.random.poisson(lam, (N,N,T))
    Forecast['vehicleArrivals'] = np.zeros((N,T))
    Forecast['driverArrivals'] = np.zeros((N,T))

    print('Setting Flags...')
    Flags = {}
    Flags['debugFlag'] = 1.
    Flags['glpkFlag'] = 0.

    print('Initializing controller...')
    c = MoDController(RoadNetwork) # instantiate our controller

    # check for infeasible start
    if (np.max(State['idleVehicles'] - RoadNetwork['parking']) >=1):
        print('ERROR: Infeasible start')
    else:
        print('Rebalancing...')
        [tasks, paths] = c.computerebalancing(Parameters, State, Forecast, Flags)

        # for k, v in output:
        #     print(k, v)

        print("\nTasks!")
        for k, v in tasks.items():
            print(k, v)

        print("\nPaths")
        for path in paths:
            print(paths)

        print('Success!')
        # print(tasks['vehicleRebalancingQueue'])
        # print(tasks['driverRebalancingQueue'])


if __name__ == '__main__':
    test()