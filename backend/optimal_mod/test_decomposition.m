N = 50;
rebalancers = 5;
T = 50;
debugFlag = 1;
% build road graph
roadGraph = {};
for i=1:N
	roadGraph{i} = 1:N;
end
% build travel times
travelTimes = zeros(N,N);
for i=1:N
	for j=1:N
		if i ~= j
			travelTimes(i,j) = abs(i-j);
		else
			travelTimes(i,j) = 1;
		end
	end
end
% get useful funcs
[Finders, statesize, numFlowVariables]  = preprocess(roadGraph, T, debugFlag);
finderMap = {};
finderMap{1} = Finders.findRoadLinkRtij;
finderMap{2} = Finders.findRoadLinkRWtij;
finderMap{3} = Finders.findRoadLinkRPtij;
finderMap{4} = Finders.findRoadLinkPVtij;
% now create shitty flows and fake paths
flows = zeros(1,statesize);
paths = {};
for r=1:rebalancers
	rebpath = {};
	t = 1;
	iidx = randi(N);
	while t < T
		% chooose i,j,t_p, reb_mode
		jidx = randi(N);
		ridx = randi(3);
		% in this case, all travel times are equal
		t_p = travelTimes(iidx, jidx) + t;
		rebpath{end + 1} = [iidx, jidx, t, t_p, ridx];
		% add to flows
		finder = finderMap{ridx};
		flows(finder(iidx,jidx,t)) = flows(finder(iidx,jidx,t)) + 1;
		% update time
		t = t_p;
		iidx = jidx;
	end
	paths{end + 1} = rebpath;
end
% get the computed paths
computedPaths = get_paths(T, flows, travelTimes, N, Finders);	

