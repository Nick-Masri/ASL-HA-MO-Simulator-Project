function [Finders, stateSize, numFlowVariables] = preprocess(roadGraph, T, debugFlag)
	%% returns the indexing "finders"
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
    stateSize= T*E + T*E + T*E + T*E + T*E + T*E;
    % flow va
    numFlowVariables = T*E + T*E + T*E + T*E + T*E + T*E;
    
    
    if debugFlag
        fprintf('State size: %d, of which %d are flow variables \n',stateSize, numFlowVariables)
    end
    
    
    Finders.findRoadLinkCtij = @(i,j,t) (t-1)*E +cumRoadNeighbors(i) + roadNeighborCounter(i,j); % C = customer 
    Finders.findRoadLinkRtij = @(i,j,t)  T*E + (t-1)*E + cumRoadNeighbors(i) + roadNeighborCounter(i,j); % R = Rebalancing flow
    Finders.findRoadLinkRWtij = @(i,j,t) T*E + T*E + (t-1)*E + cumRoadNeighbors(i) + roadNeighborCounter(i,j); % RW = Rebalancer walking
    Finders.findRoadLinkRPtij = @(i,j,t) T*E + T*E + T*E + (t-1)*E + cumRoadNeighbors(i) + roadNeighborCounter(i,j); % RP = Rebalancer Passenger (in private vehicle)
    Finders.findRoadLinkPVtij = @(i,j,t) T*E + T*E + T*E + T*E + (t-1)*E + cumRoadNeighbors(i) + roadNeighborCounter(i,j); % PV = Private Vehicle 
    Finders.findDropCtij = @(i,j,t) T*E + T*E + T*E + T*E + T*E + (t-1)*E + cumRoadNeighbors(i) + roadNeighborCounter(i,j); 
end