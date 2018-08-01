% TODO: return the private vehicle tasks as well
%% get_path: returns all the tasks in the form of paths
function [paths] = get_paths(T, cplex_out, RoadNetwork, N, Finders, is_pv, staff_at_station)
	paths = {};
	for i=1:N
		for k=1:staff_at_station(i)
			[rebpath, cplex_out] = get_single_path(i, 1, {}, cplex_out, RoadNetwork, T, N, Finders, is_pv);
			if length(rebpath) > 0
				paths{end + 1} = rebpath;
			end
		end
	end
end
% get_first_outflow: returns the first nonzero flow
function [i, j, t, t_p, reb_mode] = get_first_outflow(i,t,N,RoadNetwork, cplex_out, Finders, is_pv)
	% naive implementation
	if ~is_pv
		for j=1:N
			% do not include self trips for reb vehicles!
			if i ~= j
				if cplex_out(Finders.findRoadLinkRtij(i,j,t)) > 0
					t_p = t+RoadNetwork.travelTimes(i,j);
					reb_mode = 1;
					return
				end
			end
		end
		for j=1:N
			if cplex_out(Finders.findRoadLinkRWtij(i,j,t)) > 0
				t_p = t+RoadNetwork.driverTravelTimes(i,j);
				reb_mode = 2;
				return
			end
		end
		for j=1:N
			if cplex_out(Finders.findRoadLinkRPtij(i,j,t)) > 0
				t_p = t+RoadNetwork.pvTravelTimes(i,j);
				reb_mode = 3;
				return
			end
		end
	else
		for j=1:N
			if cplex_out(Finders.findRoadLinkPVtij(i,j,t)) > 0
				t_p = t+RoadNetwork.pvTravelTimes(i,j);
				reb_mode = 4;
				return
			end
		end
	end
		
	% did not find anything
	j  = 0;
	t_p = inf;
	reb_mode = 0;
end
% get_single_path: follows a single rebalancer until the end
function [rebpath, cplex_out] = get_single_path(i, t, rebpath, cplex_out, RoadNetwork, T, N, Finders,is_pv)
	[i, j, t, t_p, reb_mode] = get_first_outflow(i, t, N, RoadNetwork, cplex_out, Finders, is_pv);
	% if no outflow found, return empty
	if reb_mode == 0
		return
	end
	%[i,j,t,t_p,reb_mode]
	% update the flows
	if reb_mode == 1
		%[i,j,t,cplex_out(Finders.findRoadLinkRtij(i,j,t)),reb_mode]
		%sum(cplex_out)
		cplex_out(Finders.findRoadLinkRtij(i,j,t)) = cplex_out(Finders.findRoadLinkRtij(i,j,t)) - 1;
	elseif reb_mode == 2
		%[i,j,t,cplex_out(Finders.findRoadLinkRWtij(i,j,t)),reb_mode]
		%sum(cplex_out)
		cplex_out(Finders.findRoadLinkRWtij(i,j,t)) = cplex_out(Finders.findRoadLinkRWtij(i,j,t)) - 1;
	elseif reb_mode == 3
		cplex_out(Finders.findRoadLinkRPtij(i,j,t)) = cplex_out(Finders.findRoadLinkRPtij(i,j,t)) - 1;
	elseif reb_mode == 4
		cplex_out(Finders.findRoadLinkPVtij(i,j,t)) = cplex_out(Finders.findRoadLinkPVtij(i,j,t)) - 1;
	end
	% check if this is a sequential wait
	if length(rebpath) > 0
		pastPath = rebpath{end};
		if pastPath(1) == pastPath(2) & i == j
			% this is a sequential wait
			rebpath{end} = [i,j, pastPath(3), t_p, reb_mode];
		else
			rebpath{end + 1} = [i, j, t, t_p, reb_mode];
		end
	else
		rebpath{end + 1} = [i, j, t, t_p, reb_mode];
	end
	% this guy rests here
	%if t_p >= T
	%	return
	%else
		[rebpath, cplex_out] = get_single_path(j, t_p, rebpath, cplex_out, RoadNetwork, T, N, Finders, is_pv);
	%end
end