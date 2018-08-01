function [Tasks, Output]=hamod(RoadNetwork,Parameters,State,Forecast,Flags)
    % COMPUTEREBALANCING Given a MoD system state and forecasted demand returns the 
    % optimal actions for the current time step.
    %
    % INPUTS:
    % - RoadNetwork is a struct, of which
    % -- RoadNetwork.roadGraph <1xN cell> is a cell array of length N representing an adjacency list of the network
    %    such that RoadNetwork.roadGraph{i} is a vector of indices corresponding to the nodes
    %    adjacent to node i.
    % -- RoadNetwork.parking <Nx1 matrix> is such that RoadNetwork.parking(i)
    %    is the total amount of parking spots at station i.     
    % -- RoadNetwork.travelTimes <NxN matrix> is such that RoadNetwork.travelTimes(i,j)
    %    is the average travel time, in discrete time steps, that it takes for a vehicle to go
    %    from the node i to node j. By convention, RoadNetwork.travelTimes(i,i) = 1.
    % -- RoadNetwork.driverTravelTimes <NxN matrix> is such that RoadNetwork.driverTravelTimes(i,j)
    %    is the average travel time, in discrete time steps, that it takes for a rebalancer to go
    %    from the node i to node j. By convention, RoadNetwork.driverTravelTimes(i,i) = 1.
    % -- RoadNetwork.pvTravelTimes <NxN matrix> is such that RoadNetwork.pvTravelTimes(i,j)
    %    is the average travel time, in discrete time steps, that it takes for a private vehicle to go
    %    from the node i to node j. By convention, RoadNetwork.pvTravelTimes(i,i) = 1.
    % -- RoadNetwork.cTravelTimes <NxN matrix> is such that RoadNetwork.cTravelTimes(i,j)
    %    is the average usage time, in discrete time steps, that elapses between when a customer who picks up a 
    %    vehicle from node i and when they return it to node j.
    % - Parameters is a struct, of which
    % -- Parameters.thor <int> is the optimization horizon in discrete time steps
    % -- Parameters.pvCap <int> is the capacity of a private vehicle.
    % -- Parameters.vehicleRebalancingCost <float> is a cost multiplier, such that 
    %    Parameters.vehicleRebalancingCost * RoadNetwork.travelTimes(i,j) is the cost of moving a vehicle, including
    %    driver costs, from node i to node j.
    % -- Parameters.driverRebalancingCost <float> is a cost multiplier, such that 
    %    Parameters.driverRebalancingCost * RoadNetwork.driverTravelTimes(i,j) is the travel cost of moving a human
    %    rebalancer from node i to node j.
    % -- Parameters.lostDemandCost <float> is a cost multiplier, such that Parameters.lostDemandCost is the cost 
    %    of losing a customer demand, i.e. the penalty incurred when a customer does not find an
    %    available vehicle.
    % - State is a struct, of which
    % -- State.idleVehicles <Nx1> is a vector such that State.idleVehicles(i) contains the 
    %    number of vehicles currently idle at node i.
    % -- State.idleDrivers <Nx1> is a vector such taht State.idleDrivers(i) contains the 
    %    number of drivers current idle at node i.
    % -- State.privateVehciles <Nx1> specifies the number of private vehicles at each station.
    % - Forecast is a struct, of which
    % -- Forecast.demand <NxNxT array> is the forecasted demand for the length
    %    of the optimizatio horizon, such that Forecast.demand(i,j,t) is the number of customers
    %    wishing to go from node i to node j at time step t.
    % -- Forecast.vehicleArrivals <NxT array> is the forecasted arrival of vehicles currently performing
    %    other tasks (e.g. customer/rebalancing trips or under maintenance), such that 
    %    Forecast.vehicleArrivals(i,t) is the number of vehicles that will be
    %    arriving to node i at time step t. 
    % -- Forecast.driverArrivals <NxT array> is the forecasted arrivals of drivers currently
    %    performing other tasks (e.g. rebalancing vehicles, traveling, or off-shift), such that
    %    Forecast.driverArrivals(i,t) is the number of driver that will be arriving to node i
    %    at time step t.
    % - Flags is a struct, of which
    % -- Flags.debugFlag <bool> indicates whether to print debugging information.
    %
    % OUTPUTS:
    % - Tasks is a struct, of which
    % -- Tasks.vehicleRebalancingQueue <Nx1 cell> is a cell array specifying the vehicle rebalancing
    %    tasks for each station to be executed at the current time step, such that 
    %    Tasks.vehicleRebalancingQueue{i}(j) is the index of the jth vehicle rebalancing task
    %    at node i.
    % -- Tasks.driverRebalancingQueue <Nx1 cell> is a cell array specifying the driver rebalancing
    %    tasks for each station to be executed at the current time step, such that 
    %    Tasks.driverRebalancingQueue{i}(j) is the index of the jth driver rebalancing task
    %    at node i.
    % - Output is a struct which contains the output information from the CPLEX solver 
    %   (see the CPLEX documentation for more information).
    %
    % Notes and Assumptions:
    % - Currently, it assumes that idle drivers and idle vehicles incurr no cost.
    % - Current implementation prefers clarity over efficiency, future, production code could
    %   potentially gain significant efficiency.

    % addpath('C:\Program
    % Files\IBM\ILOG\CPLEX_Studio1271\cplex\matlab\x64_win64'); % windows 
    % addpath('/opt/ibm/ILOG/CPLEX_Studio128/cplex/matlab/x86-64_linux') % ubuntu
    %% Unpack variables


    roadGraph=RoadNetwork.roadGraph;
    parking=RoadNetwork.parking; % max capacity parking spaces. 
    travelTimes=RoadNetwork.travelTimes;
    driverTravelTimes=RoadNetwork.driverTravelTimes;
    pvTravelTimes=RoadNetwork.pvTravelTimes;
    cTravelTimes=RoadNetwork.cTravelTimes;

    T=Parameters.thor;
    pvCap = Parameters.pvCap; % Matt added this.
    vehicleRebalancingCost = Parameters.vehicleRebalancingCost;
    driverRebalancingCost = Parameters.driverRebalancingCost;
    pvRebalancingCost = Parameters.pvRebalancingCost; % Matt added this. 
    lostDemandCost  = Parameters.lostDemandCost;
    

    idleVehicles = State.idleVehicles;
    idleDrivers = State.idleDrivers;
    privateVehicles = State.privateVehicles; % Matt added this.
    
    demand = round(Forecast.demand);
    vehicleArrivals = Forecast.vehicleArrivals;
    driverArrivals = Forecast.driverArrivals; 
    unroundDemand = Forecast.demand;

    debugFlag = Flags.debugFlag;
    glpkFlag = Flags.glpkFlag;
    if debugFlag
        fprintf('Optimization horizon: %d \n', T)
    end

    % check for violations
    dpark = parking - idleVehicles - sum(vehicleArrivals,2)';
    if min(dpark) < 0
        % somthing's wrong
        disp('Parking violated!\n');
        dpark
    end


    %% Preprocessing work
    for i=1:length(roadGraph)
        roadGraph{i}=sort(unique(roadGraph{i}));
    end

    reverseRoadGraph=cell(size(roadGraph));
    for i=1:length(roadGraph)
        for j=roadGraph{i}
            reverseRoadGraph{j}=[reverseRoadGraph{j} i];
        end
    end
    for i=1:length(reverseRoadGraph)
        reverseRoadGraph{i}=sort(unique(reverseRoadGraph{i}));
    end

    N=length(roadGraph);

    E=0;
    numRoadEdges=zeros(N,1);
    for i=1:N
        numRoadEdges(i)=length(roadGraph{i});
        E=E+length(roadGraph{i});
    end
    cumRoadNeighbors=cumsum(numRoadEdges);
    cumRoadNeighbors=[0;cumRoadNeighbors(1:end-1)];
    
    roadNeighborCounter=sparse([],[],[],N,N,E);
    tempNeighVec=zeros(N,1);
    for i=1:N
        for j=roadGraph{i}
            tempNeighVec(j)=1;
        end
        neighCounterLine=cumsum(tempNeighVec);
        for j=roadGraph{i}
            roadNeighborCounter(i,j)=neighCounterLine(j);
        end
        tempNeighVec=zeros(N,1);
    end

    %% Build finders
    % statesize consists of driver variables, rebalancing variables
    % customer variables and los demand variables
    stateSize= 6*T*E + 2*T*N;
    % flow va
    numFlowVariables = 6*T*E;
    
    
    if debugFlag
        fprintf('State size: %d, of which %d are flow variables \n',stateSize, numFlowVariables)
    end
    
    
    findRoadLinkCtij = @(i,j,t) 0*T*E + (t-1)*E +cumRoadNeighbors(i) + roadNeighborCounter(i,j); % C = customer 
    findRoadLinkRtij = @(i,j,t)  1 * T*E + (t-1)*E + cumRoadNeighbors(i) + roadNeighborCounter(i,j); % R = Rebalancing flow
    findRoadLinkRWtij = @(i,j,t) 2 * T*E+ (t-1)*E + cumRoadNeighbors(i) + roadNeighborCounter(i,j); % RW = Rebalancer walking
    findRoadLinkRPtij = @(i,j,t) 3 * T*E + (t-1)*E + cumRoadNeighbors(i) + roadNeighborCounter(i,j); % RP = Rebalancer Passenger (in private vehicle)
    findRoadLinkPVtij = @(i,j,t) 4 * T*E + (t-1)*E + cumRoadNeighbors(i) + roadNeighborCounter(i,j); % PV = Private Vehicle 
    findDropCtij = @(i,j,t) 5 * T*E + (t-1)*E + cumRoadNeighbors(i) + roadNeighborCounter(i,j); 
    findDemandMismatchit = @ (i,t) 6 * T*E + 0 * T*N + (t-1)*N + i;
    findParkingMismatchit = @ (i,t) 6 * T*E + 1 * T*N +  (t-1)*N + i;
    
    %% Build costs
    if debugFlag
        fprintf('Building cost...')
    end
    fCost=zeros(stateSize,1);
    epsilon = 0.0;

    for i=1:N
        for t=1:T
            for j=roadGraph{i}
                % rebalancing costs
                if i ~= j
                    fCost(findRoadLinkRtij(i,j,t))= vehicleRebalancingCost*travelTimes(i,j);
                    fCost(findRoadLinkRWtij(i,j,t))= driverRebalancingCost*driverTravelTimes(i,j); 
                    % no cost for passenger rebalancers. Instead, we impose
                    % a cost on moving the private vehicle instead. 
                    
                    % (1 + t*epsilon) is just to encourage the pv to move
                    % first then wait, as opposed to wait and then move. 
                    fCost(findRoadLinkPVtij(i,j,t))= (1 + t*epsilon)*pvRebalancingCost*pvTravelTimes(i,j); % moving cost for private vehicle 
                end
                % driver 
                % waiting costs
                fCost(findDropCtij(i,j,t))= lostDemandCost;
            end
            fCost(findDemandMismatchit(i,t))= lostDemandCost;
            fCost(findParkingMismatchit(i,t))= lostDemandCost;
        end
    end

    %% Initialize constraints
    if debugFlag
        disp('Initializing constraints...')
    end
    
    %% Build equality constraints
    
    if debugFlag
        disp('Building sparse equality constraints... \n')
    end
    
    % number of equality constraints is T*N*N for customer travel
    % T*N for conservation of vehicles
    % T*N for conservation of drivers
    % T*N for conservation of private vehicle 
    % T*N for parking constraints
    
    n_eq_constr = T*N*N + T*N + T*N + T*N;
    n_eq_entries = T*N*N*2 + T*N*N*4 + T*N*N*6 + T*N*N*2;
    
    Aeqsparse=zeros(n_eq_entries,3);
    Beq=zeros(n_eq_constr,1);
    Aeqrow=1;
    Aeqentry=1;


    if debugFlag
        fprintf('Building LP program with statesize %d,%d equality constraints with %d entries \n', ...
            stateSize,n_eq_constr, n_eq_entries)
    end
    % Conservation of rebalancers
    if debugFlag
        disp('Building road map for rebalancers')
        [a,b,c] = size(demand);
        fprintf('demand size: %d,%d,%d',a,b,c)
        fprintf('Time step: ')
    end
    for t=1:T
        if debugFlag
            fprintf(' %d/%d ',t,T)
        end
        for i=1:N
                % i) cust constraints
                if ~isempty(roadGraph{i})
                    for j=roadGraph{i} 
                        %Out-flows, cust embark to their destination
                        Aeqsparse(Aeqentry,:)=[Aeqrow,findRoadLinkCtij(i,j,t), 1];
                        Aeqentry=Aeqentry+1;
                        % lost demand
                        Aeqsparse(Aeqentry,:)=[Aeqrow,findDropCtij(i,j,t), 1];
                        Aeqentry=Aeqentry+1;
                        % all of this must equal the predicted demand for (t,i,j)
                        % and we want this to equal the total amount of demand at that time and node
                        Beq(Aeqrow)= demand(i,j,t);
                        Aeqrow=Aeqrow+1;
                    end
                end
                % ii) vehicle constraints
                if ~isempty(roadGraph{i})
                    for j=roadGraph{i} %Out-flows
                         % rebalancing outlfows
                         Aeqsparse(Aeqentry,:)=[Aeqrow,findRoadLinkRtij(i,j,t), 1];
                         Aeqentry=Aeqentry+1;
                         % cust outflows
                         Aeqsparse(Aeqentry,:)=[Aeqrow,findRoadLinkCtij(i,j,t), 1];
                         Aeqentry=Aeqentry+1;
                    end
                end
                if ~isempty(reverseRoadGraph{i})
                    for j=reverseRoadGraph{i} %In-flows
                        if (travelTimes(j,i) < t)
                            % rebalancing inflows
                            Aeqsparse(Aeqentry,:)=[Aeqrow,findRoadLinkRtij(j,i,t - travelTimes(j,i)),-1];
                            Aeqentry=Aeqentry+1;
                        end
                        if (cTravelTimes(j,i) < t)
                            % cust inflows
                            Aeqsparse(Aeqentry,:)=[Aeqrow,findRoadLinkCtij(j,i,t - cTravelTimes(j,i)), -1];
                            Aeqentry=Aeqentry+1;
                        end
                    end
                end
                if t == 1
                    Beq(Aeqrow)= idleVehicles(i);
                else
                    Beq(Aeqrow)= vehicleArrivals(i,t);
                end
                Aeqrow=Aeqrow+1;
                % iii) driver constraints
                if ~isempty(roadGraph{i})
                    for j=roadGraph{i} %Out-flows
                        if i~=j
                            % rebalancing outlfows
                            Aeqsparse(Aeqentry,:)=[Aeqrow,findRoadLinkRtij(i,j,t), 1]; % outbound rebalancers via a ha:mo
                            Aeqentry=Aeqentry+1;
                            Aeqsparse(Aeqentry,:)=[Aeqrow,findRoadLinkRPtij(i,j,t), 1]; % outbound rebalancers via private vehicle 
                            Aeqentry=Aeqentry+1;
                        end
                        % driver outflows
                        Aeqsparse(Aeqentry,:)=[Aeqrow,findRoadLinkRWtij(i,j,t), 1]; % outbound rebalancers via foot/bike
                        Aeqentry=Aeqentry+1;
                    end
                end
                if ~isempty(reverseRoadGraph{i})
                    for j=reverseRoadGraph{i} %In-flows
                        if (travelTimes(j,i) < t) & i~=j
                            % rebalancing inflows
                            Aeqsparse(Aeqentry,:)=[Aeqrow,findRoadLinkRtij(j,i,t - travelTimes(j,i)),-1]; % incoming rebalancers via a ha:mo
                            Aeqentry=Aeqentry+1;
                        end
                        
                        if (pvTravelTimes(j,i) < t) & i~=j
                            % rebalancing inflows
                            Aeqsparse(Aeqentry,:)=[Aeqrow,findRoadLinkRPtij(j,i,t - pvTravelTimes(j,i)),-1]; % incoming rebalancers via the private vehicle 
                            Aeqentry=Aeqentry+1;
                        end
                        
                        if (driverTravelTimes(j,i) < t)
                            % cust inflows
                            Aeqsparse(Aeqentry,:)=[Aeqrow,findRoadLinkRWtij(j,i,t - driverTravelTimes(j,i)), -1]; % incoming rebalancers via foot/bike 
                            Aeqentry=Aeqentry+1;
                        end
                    end
                end
                if t == 1
                    Beq(Aeqrow)= idleDrivers(i);
                else
                    Beq(Aeqrow) = driverArrivals(i,t);
                end
                Aeqrow=Aeqrow+1;
                
                % iv) private vehicle continuity
                
                if ~isempty(roadGraph{i})
                    for j=roadGraph{i}
                        % PV outlfows
                        Aeqsparse(Aeqentry,:)=[Aeqrow,findRoadLinkPVtij(i,j,t), 1];
                        Aeqentry=Aeqentry+1;
                        
                    end
                end
                if ~isempty(reverseRoadGraph{i})
                    for j=reverseRoadGraph{i}
                        if (pvTravelTimes(j,i) < t) 
                            % PV inflows
                            Aeqsparse(Aeqentry,:)=[Aeqrow,findRoadLinkPVtij(j,i,t - pvTravelTimes(j,i)), -1];
                            Aeqentry=Aeqentry+1;
                        end
                    end
                end
                if t == 1
                    Beq(Aeqrow) = privateVehicles(i);
                else
                    Beq(Aeqrow) = 0; % redundant, but easy to read
                end
                Aeqrow = Aeqrow + 1;
                
                
        end
    end

    if Aeqrow-1~=n_eq_constr
        %fprintf('ERROR: unexpected number of equality constraints (expected: %d, actual: %d)\n',n_eq_constr,Aeqrow-1)
    end
    if Aeqentry-1~=n_eq_entries
      %  fprintf('Warning: unexpected number of equality entries (expected: %d, actual: %d)\n',n_eq_entries,Aeqentry-1)
    end
    
    if debugFlag
        disp('Building matrices from sparse representation')
    end

    Aeqsparse=Aeqsparse(1:Aeqentry-1,:);
    Aeq=sparse(Aeqsparse(:,1),Aeqsparse(:,2),Aeqsparse(:,3), Aeqrow-1, stateSize);

    %% Build inequality constraints
    
    if debugFlag
        disp('Building sparse inequality constraints... \n')
    end   
    
    % Find out how many entries needed for parking
    n_entries_parking = 0;
    for i = 1:N
        for j = 1:N
            if (cTravelTimes(j,i) < T)
                n_entries_parking = n_entries_parking + cTravelTimes(j,i)*(T - cTravelTimes(j,i)); % full effect
                n_entries_parking = n_entries_parking + cTravelTimes(j,i)*(cTravelTimes(j,i)-1)/2; % edge effects
            else
                n_entries_parking = n_entries_parking + T*(T-1)/2;
            end
        end
    end
    %fprintf('Clever: %d \n', n_entries_parking)
    %{
    n_entries_parking = 0;
    for t = 1:T
        for i = 1:N
            for j = 1:N
                for s=1:t-1
                    if (s + cTravelTimes(j,i) >= t) % started but not yet finished
                        n_entries_parking = n_entries_parking + 1;
                    end    
                end
            end
        end
    end
    %fprintf('Naive: %d \n', n_entries_parking)
    %}
    
    % N*N*T constraints for private vehicle capacity.
    % each constraint has 2 entries, thus 2*N*N*T inequality entries 
    % demand mismatch: N*T ineq constr, 4*N*N*T ineq entries
    % parking mismatch: N*T ineq constr, 2*N*N*T ineq entries

    
    n_ineq_constr = N*N*T + N*T + N*T + N*T;
    n_ineq_entries = 2*N*N*T + 2*n_entries_parking + 4*N*N*T + 2*N*N*T;
    
    Aineqsparse = zeros(n_ineq_entries, 3);
    Bineq = zeros(n_ineq_constr, 1);
    Aineqrow = 1;
    Aineqentry = 1;
    
    if debugFlag
        fprintf('Building LP program with statesize %d,%d inequality constraints with %d entries \n', ...
            stateSize,n_ineq_constr, n_ineq_entries)
    end
    
    
    for t = 1:T
        for i = 1:N
            % iv) private vehicle capacity constraints. 
            if ~isempty(roadGraph{i})
                for j = roadGraph{i}
                    % number of rebalancers riding PV from i to j at time t
                    Aineqsparse(Aineqentry,:) = [Aineqrow, findRoadLinkRPtij(i,j,t), 1];
                    Aineqentry = Aineqentry + 1;
                    
                    % PV flow from i to j at time t.
                    Aineqsparse(Aineqentry,:) = [Aineqrow, findRoadLinkPVtij(i,j,t), -pvCap];
                    Aineqentry = Aineqentry + 1;
                    
                    Aineqrow = Aineqrow + 1;
                end 
            end
            
            % v) parking constraints
            % NOTE: We may be doing something wrong for t=1. I don't think
            % it is a problem but if you see buggy behavior in the future
            % then consider this as a potential issue.
            if ~isempty(reverseRoadGraph{i})
                for j=reverseRoadGraph{i}
                    for s = 1:t-1
                        if (s + cTravelTimes(j,i) >= t)
                            Aineqsparse(Aineqentry,:) = [Aineqrow,findRoadLinkCtij(j,i,s),1];
                            Aineqentry = Aineqentry + 1;
                        end
                        if (s + travelTimes(j,i) >= t)
                            Aineqsparse(Aineqentry,:) = [Aineqrow,findRoadLinkRtij(j,i,s),1];
                            Aineqentry = Aineqentry + 1;
                        end
                    end
                end
            end
            Bineq(Aineqrow) = parking(i) - sum(vehicleArrivals(i,t:T));
            Aineqrow = Aineqrow + 1;

            % vi) demand mismatch
            % demand mismatch penalty
            Aineqsparse(Aineqentry,:) = [Aineqrow, findDemandMismatchit(i,t), -1];
            Aineqentry = Aineqentry + 1;
            if ~isempty(roadGraph{i})
                for j = roadGraph{i}
                    % reb flow out, only if heading elsewhere
                    if i~=j
                        Aineqsparse(Aineqentry,:) = [Aineqrow, findRoadLinkRtij(i,j,t), 1];
                        Aineqentry = Aineqentry + 1;
                    end
                end
            end
            if ~isempty(reverseRoadGraph{i})
                for j = reverseRoadGraph{i}
                    % reb flow in, only if it arrives now
                    if (travelTimes(j,i) < t)
                        Aineqsparse(Aineqentry,:) = [Aineqrow, findRoadLinkRtij(j,i,t - travelTimes(j,i)),-1];
                        Aineqentry = Aineqentry + 1;
                    end
                    % cust flow in, only if it arrives now
                    if (cTravelTimes(j,i) < t)
                        Aineqsparse(Aineqentry,:) = [Aineqrow, findRoadLinkCtij(j,i,t - cTravelTimes(j,i)),-1];
                        Aineqentry = Aineqentry + 1;
                    end

                end
            end
            % bineq must have the sum of demand
            if t < T
                Bineq(Aineqrow) = -sum(unroundDemand(i,:,t));
            else
                % if the forecasted demand is higher, bundle it up
                Bineq(Aineqrow) = -sum(sum(unroundDemand(i,:,t:end)));
            end
            Aineqrow=Aineqrow+1;

            % vii) parking mismatch
            % parking mismatch penalty
            Aineqsparse(Aineqentry,:) = [Aineqrow, findParkingMismatchit(i,t), -1];
            Aineqentry = Aineqentry + 1;
            if ~isempty(reverseRoadGraph{i})
                for j = reverseRoadGraph{i}
                    % reb flow in, only if it arrives now
                    if (travelTimes(j,i) < t)
                        Aineqsparse(Aineqentry,:) = [Aineqrow, findRoadLinkRtij(j,i,t - travelTimes(j,i)),1];
                        Aineqentry = Aineqentry + 1;
                    end
                end
            end
            % bineq must have the sum of demand
            % compute the arriving demand first
            dit = 0;
            if ~isempty(reverseRoadGraph{i})
                for j = reverseRoadGraph{i}
                    for s = 1:t-1
                        if (s + cTravelTimes(j,i) >= t)
                            dit = dit + unroundDemand(j,i,s);
                        end
                    end
                end
            end
            if t < T
                Bineq(Aineqrow) = parking(i) - dit;
            else
                % bundle future demand together
                Bineq(Aineqrow) = parking(i) - dit - sum(sum(unroundDemand(:,i,t+1:end)));
            end
            Aineqrow=Aineqrow+1;
        end
    end
    
    if Aineqrow-1~=n_ineq_constr
        %fprintf('ERROR: unexpected number of inequality constraints (expected: %d, actual: %d)\n',n_ineq_constr,Aineqrow-1)
    end
    if Aineqentry-1~=n_ineq_entries
        %fprintf('Warning: unexpected number of inequality entries (expected: %d, actual: %d)\n',n_ineq_entries,Aineqentry-1)
    end
    
    if debugFlag
        disp('Building matrices from sparse representation')
    end

    Aineqsparse=Aineqsparse(1:Aineqentry-1,:);
    Aineq=sparse(Aineqsparse(:,1),Aineqsparse(:,2),Aineqsparse(:,3), Aineqrow-1, stateSize);
    
    %% Upper and lower bounds
    if debugFlag
        disp('Building upper and lower bounds')
    end
    lb=zeros(stateSize,1); %everything is non-negative
    ub=Inf*ones(stateSize,1); %no constraints

    % test if any of constraints are non-integer
    dff1 = max(abs(round(Beq) - Beq));
    dff2 = max(abs(round(Bineq) - Bineq));
    if dff1 > 0 || dff2 > 0
        fprintf('Non-int constraint! %d, %d', dff1, dff2)
    end

    %% Call optimizer
    if debugFlag
        disp('Calling optimizer')
    end

    %% Variable type
    if debugFlag
        disp('Building constraint type')
    end
    ConstrType=char(zeros(1,stateSize));
    ConstrType(1:end)='I';
    % set only the drop demand as float
    for t=1:T
        for i=1:N
            for j=1:N
                ConstrType(findDropCtij(i,j,t)) = 'C';
            end
            ConstrType(findDemandMismatchit(i,t)) = 'C';
            ConstrType(findParkingMismatchit(i,t)) = 'C';
        end
    end
    % set only the private vehicle as int
    %for i=1:N
    %    for j=1:N
    %        for t=1:T
    %            ConstrType(findRoadLinkPVtij(i,j,t)) = 'I';
    %        end
    %    end
    %end

    if debugFlag
        fprintf('Solving as MILP.')
    end
    MyOptions=cplexoptimset('cplex');;
    %MyOptions.parallel=1;
    %MyOptions.threads=8;
    %MyOptions.mip.tolerances.mipgap=0.05;
    % MyOptions.emphasis.mip = 0;
    MyOptions.Display = 'iter';
    if debugFlag
        tic
    end
    if ~glpkFlag
        [cplex_out,fval,exitflag,output]=cplexmilp(fCost,Aineq,Bineq,Aeq,Beq,[],[],[],lb,ub,ConstrType,[],MyOptions);
    else
        neq = size(Aeq,1);
        ctype = char(zeros(1,neq));
        ctype(1:end)='S';
        sense = 1;
        [cplex_out, fval, exitflag, output]=glpk (fCost, Aeq, Beq, lb, ub, ctype, ConstrType, sense);
    end
    %[cplex_out,fval,exitflag,output]=intlinprog(fCost,1:stateSize,[],[],Aeq,Beq,lb,ub);
    if debugFlag
        toc
    end
    if debugFlag
        fprintf('CPLEX: Solved! fval: %f\n', fval)
        disp(output)
        %fprintf('GLPK: Solved! fval: %f\n', fval2)
        %disp(output2)
        %fprintf('Solution difference: %f\n', norm(cplex_out-cplex_out2))
    end
    % if it failed
    if output.cplexstatus == 103
        cplex_out = zeros(size(fCost));
    end
    if debugFlag
        served = 0;
        dropped = 0;
        demand_mismatch = 0;
        parking_mismatch = 0;
        for t=1:T
            for i=1:N
                for j=1:N
                    served = served + cplex_out(findRoadLinkCtij(i,j,t));
                    dropped = dropped + cplex_out(findDropCtij(i,j,t));
                end
                demand_mismatch = demand_mismatch + cplex_out(findDemandMismatchit(i,t));
                parking_mismatch = parking_mismatch + cplex_out(findParkingMismatchit(i,t));
            end
        end
        fprintf('Total served: %f\n', served)
        fprintf('Total dropped: %f\n', dropped)
        fprintf('Total demand mismatch: %f\n', demand_mismatch)
        fprintf('Total parking mismatch: %f\n', parking_mismatch)
    end
    % build queues
    %fprintf('Max difference: %d \n',max(abs(round(cplex_out) - cplex_out)));
    %cplex_out = round(cplex_out);
    vehicleRebalancingQueue = cell(N,1);
    for i = 1:N
        for j = 1:N
            if i ~= j
                for k = 1:cplex_out(findRoadLinkRtij(i,j,1))
                    vehicleRebalancingQueue{i} = [vehicleRebalancingQueue{i} j];
                end
            end
        end
    end
    driverRebalancingQueue = cell(N,1);
    for i = 1:N
        for j = 1:N
            if i ~= j
                for k = 1:cplex_out(findRoadLinkRWtij(i,j,1))
                    driverRebalancingQueue{i} = [driverRebalancingQueue{i} j];
                end
            end
        end
    end
    driverPassengerRebalancingQueue = cell(N,1); % rebalancers riding in PV
    for i = 1:N
        for j = 1:N
            if i ~= j
                for k = 1:cplex_out(findRoadLinkRPtij(i,j,1))
                    driverPassengerRebalancingQueue{i} = [driverPassengerRebalancingQueue{i} j];
                end
            end
        end
    end
    privateVehicleRebalancingQueue = cell(N,1); % private vehicle movement
    for i = 1:N
        for j = 1:N
            if i ~= j
                for k = 1:cplex_out(findRoadLinkPVtij(i,j,1))
                    privateVehicleRebalancingQueue{i} = [privateVehicleRebalancingQueue{i} j];
                end
            end
        end
    end
    if debugFlag
        G = digraph();
        for i = 1:N
            for j = 1:N
                w = 0;
                for t = 1:T
                    w = w + cplex_out(findRoadLinkRtij(i,j,t));
                end
                if w > 0
                    G = addedge(G,i,j,w);
                end
            end
        end
        %plot(G);
    end
    Tasks.vehicleRebalancingQueue = vehicleRebalancingQueue;
    Tasks.driverRebalancingQueue = driverRebalancingQueue;
    Tasks.driverPassengerRebalancingQueue = driverPassengerRebalancingQueue;
    Tasks.privateVehicleRebalancingQueue = privateVehicleRebalancingQueue;
    Output = output;
    Output.cplex_out = cplex_out;
    Finders.findRoadLinkCtij = findRoadLinkCtij;
    Finders.findRoadLinkRtij = findRoadLinkRtij;
    Finders.findRoadLinkRWtij = findRoadLinkRWtij;
    Finders.findRoadLinkRPtij = findRoadLinkRPtij;
    Finders.findRoadLinkPVtij = findRoadLinkPVtij;
    Finders.findDropCtij = findDropCtij;
    [paths] = get_paths(T, cplex_out, RoadNetwork, N, Finders, 0, idleDrivers);
    [pvPaths] = get_paths(T, cplex_out, RoadNetwork, N, Finders, 1, privateVehicles);
    % there must be a better way
    for p=1:length(pvPaths)
        paths{end + 1} = pvPaths{p};
    end
    % assert that constraints are satisfied
    sum(Aeq * cplex_out == Beq)
    sum(Aineq * cplex_out <= Bineq)
end
