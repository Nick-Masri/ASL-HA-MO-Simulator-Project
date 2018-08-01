% Tests MPC
addpath('/opt/ibm/ILOG/CPLEX_Studio128/cplex/matlab/x86-64_linux')
MyOptions=cplexoptimset('cplex');

numVehicles = 100;
numDrivers = 5;
N = 30;
T = 16;
avgDemandPerStation = 1;
parking_capacity = 2*avgDemandPerStation*ceil(T/2);
fprintf('Total Capacity: %d', N*parking_capacity)

roadGraph = cell(N,1);
%% Build a random road graph
for i=1:N
    roadGraph{i} = [1:N];
end
% the graph lives in a coordinate space of T by T time steps
coords = rand(N,2) * T/2;
parking = parking_capacity*ones(N,1); % add maximum parking 
travelTimes = squareform(pdist(coords));
driverTravelTimes = travelTimes*1; % vehicle 1x faster
travelTimes(logical(eye(size(travelTimes)))) = 1;
driverTravelTimes(logical(eye(size(driverTravelTimes)))) = 1;

RoadNetwork.roadGraph = roadGraph;
RoadNetwork.parking = parking;
RoadNetwork.travelTimes = ceil(travelTimes);
RoadNetwork.driverTravelTimes = ceil(driverTravelTimes);
RoadNetwork.pvTravelTimes = RoadNetwork.travelTimes;
RoadNetwork.cTravelTimes = 2*RoadNetwork.travelTimes; % users take longer

Parameters.thor = T;
Parameters.pvCap = 4; % capacity of private vehicle 
Parameters.vehicleRebalancingCost = 3;
Parameters.pvRebalancingCost = 3; % cost to drive PV is same as ha:mo. 
Parameters.driverRebalancingCost = 2;
Parameters.lostDemandCost = 1e4;


State.idleVehicles = zeros(N,1);
State.idleDrivers = zeros(N,1);
State.privateVehicles = zeros(N,1)
State.privateVehicles(unidrnd(N,1)) =1 % place the private vehicle randomly.

Forecast.demand = zeros(N,N,T);
Forecast.vehicleArrivals = zeros(N,T);
Forecast.driverArrivals = zeros(N,T);

Flags.debugFlag = 1;
Flags.glpkFlag = 0;

% placing the vehicles and drivers randomly
Tinit = ceil( 0.5*T );
V = rand(numVehicles,2);
V(:,1) = ceil(V(:,1) * N);
% V(:,2) = ceil(V(:,2) .^2 * Tinit);
V(:,2) = ones(numVehicles,1); % debugging
D = rand(numDrivers,2);
D(:,1) = ceil(D(:,1) * N); % selects location
D(:,2) = ceil(D(:,2) .^2 * Tinit); % selects time

% We may need to make sure the state at time 0 does no exceed parking. 

for t=1:Tinit
    for i=1:N
        vehMask = V(:,1) == i & V(:,2) == t;
        driverMask = D(:,1) == i & D(:,2) == t;
        if t > 1
            Forecast.vehicleArrivals(i,t) = sum(vehMask);
            Forecast.driverArrivals(i,t) = sum(driverMask);
        else
            State.idleVehicles(i) = sum(vehMask);
            State.idleDrivers(i) = sum(driverMask);
        end
    end
end

for i = 1:N
    if (State.idleVehicles(i) > parking(i))
        fprintf('ERROR: infeasible start. \n')
    end
end

% random demand
Forecast.demand(:,:,1:Tinit) = poissrnd(avgDemandPerStation / N, N, N, Tinit);

% RoadNetwork.parking = State.idleVehicles; % debugging purposes 
% [Tasks, Output]=computerebalancing(RoadNetwork,Parameters,State,Forecast,Flags);
% [Tasks, Output]=CR_cust_times(RoadNetwork,Parameters,State,Forecast,Flags); % compute rebalancing with customer times neq rebalance times
% [Tasks, Output]=hamod_noparking(RoadNetwork,Parameters,State,Forecast,Flags);
[Tasks, Output]=hamod(RoadNetwork,Parameters,State,Forecast,Flags);

%% plot rebalancing tasks for first time step
Gv = digraph(zeros(N,N));
Gd = digraph(zeros(N,N));
for t=length(Tasks)
    % each task is a full path for a specific dude
    firstTask = Tasks{t}{1};
    i = firstTask(1);
    j = firstTask(2);
    reb_mode = firstTask(5);
    if reb_mode == 1
        if findedge(Gv,i,j) > 0
            w = Gv.Edges.Weight(findedge(Gv,i,j));
            Gv.Edges.Weight(findedge(Gv,i,j)) = w+1;
        else
            Gv = addedge(Gv,i,j,1);
        end
    elseif reb_mode ~= 4
        if findedge(Gd,i,j) > 0
            w = Gd.Edges.Weight(findedge(Gd,i,j));
            Gd.Edges.Weight(findedge(Gd,i,j)) = w+1;
        else
            Gd = addedge(Gd,i,j,1);
        end
    end
end

figure;
subplot(2,1,1);
plot(Gv,'XData',coords(:,1),'YData',coords(:,2));
title('Vehicle Rebalancing');

subplot(2,1,2);
plot(Gd,'XData',coords(:,1),'YData',coords(:,2));
title('Driver Rebalancing')
