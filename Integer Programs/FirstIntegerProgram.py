import gurobipy as gp
from gurobipy import *
from gurobipy import GRB
import numpy as np
import scipy.linalg as spla
import pandas as pd
import itertools
from matplotlib import pyplot as plt
import string
import math as math



elevation_frame = pd.read_csv(r"C:\Users\philm\Documents\456\elev_diffs_2.csv")

distance_frame = pd.read_csv(r"C:\Users\philm\Documents\456\dist_diff_3.csv")

trash_frame = pd.read_csv(r"C:\Users\philm\Documents\456\trash_list(cs)_2.csv")

ids = trash_frame.id
ids = ids.drop_duplicates()
ids.reset_index(inplace = True, drop = True)
print(ids)
""" FINDING TOTAL COLLECTION AMOUNTS """

trash_vol = trash_frame.trash
paper_vol = trash_frame.paper
container_vol = trash_frame.containers
compost_vol = trash_frame.compost

total_volume_by_id = {}

##We exclude trash waste because that is kept in another trailer of the bike and does not fill up first typically
for (trash, paper, containers, compost, id) in zip(trash_vol, paper_vol, container_vol, compost_vol, ids):
    total_volume_by_id[id] = paper + containers + compost


""" END COLLECTION AMOUNTS"""

""" CREATING TIME ARRAY """
distance_arr = np.array(distance_frame)
elevation_arr = np.array(elevation_frame)
time_per_edge_arr = distance_arr

row_count = 0
col_count = 0

##Bike is moving 10mph

for row in time_per_edge_arr:
    for col_count in range(0,985):
        if(col_count < 985) and (row_count < 985):
            time_per_edge_arr[row_count][col_count] = time_per_edge_arr[row_count][col_count]/10
    row_count += 1
    
##Time array between all houses if biking between them
t = time_per_edge_arr
""" END TIME ARRAY"""

route_ids = trash_frame.route_id

routes_container_raw_vals = {}
routes_container_house_ids = {}

for route_id, house_id in zip(route_ids, ids):
    route_id = str(route_id)
    if(route_id in routes_container_house_ids):
        routes_container_raw_vals[route_id]  = routes_container_raw_vals[route_id] + 1
        routes_container_house_ids[route_id].append(house_id)
    else:
        routes_container_raw_vals[route_id] = 1
        routes_container_house_ids[route_id] = []
        routes_container_house_ids[route_id].append(house_id)

id_to_index = {}

count =  0

for id in ids:
    id_to_index[str(id)] = count
    count += 1
route_times = {}



##We store all the optimal time values for each route id in the dictionary route_times by running the integer program in this loop.

for route in routes_container_house_ids.keys():
    m=gp.Model()
    
    ##All the houses in a route given by the index in the matrix of the values for distance, elevation and so on above
    houses = []
    for house in routes_container_house_ids[route]:
        if house == 1:
            continue
        if house == 2:
            continue
        else:
            houses.append(house)
    ##The two collection centers are put in the first two indices of the houses list
    houses.insert(0, 1)
    houses.insert(1, 2)
    
    ##Variables
    x = m.addVars(len(houses), len(houses), vtype=GRB.BINARY, name = "x")
    r = m.addVar(vtype = GRB.INTEGER)
    u = m.addVars(len(houses), vtype=GRB.INTEGER)
    
    obj=0
    for i in range(0,len(houses)):
        for j in range(0,len(houses)):
            obj+= t[id_to_index[str(int(houses[i]))]][id_to_index[str(int(houses[j]))]]*x[i,j]
    m.setObjective(obj, GRB.MINIMIZE)
    
    
    ##Constraints
    
    ##For each house there is a path in and out
    ##We start at 2 because we do not want to include collection centers
    ##Outgoing
    m.addConstrs((gp.quicksum(x[i,j]for j in range(0, len(houses)))==1 for i in range(2, len(houses))))
        
    ##Ingoing
    m.addConstrs((gp.quicksum(x[j,i] for j in range(0, len(houses)))==1 for i in range(2, len(houses))))
    
    
    ##Constraint for how many edges we can have leaving and entering the collection centers
    res4=0
    res5=0
    for i in range(2,len(houses)):
        res4+=x[0,i]
        res4+=x[1,i]
        res5+=x[i,0]
        res5+=x[i,1]
    m.addConstr(res4==r)
    m.addConstr(res5==r)
    
    ##We need a constraint saying that there must be at least one run
    m.addConstr(r>=1)
    
    ##Constraint saying a bike cannot go from one house to the same house
    for i in range(0, len(houses)):
        for j in range(0, len(houses)):
            if (i ==j):
                m.addConstr(x[i,j]==0)

    ##We set up the constraint to make sure each run ends at a collection center and a bike does not get overly full (<216 gallons)
    for i in range(2,len(houses)):
        for j in range(2, len(houses)):
            if j !=i:
                m.addConstr(u[j]-u[i] + 216*(1-x[i,j])>= total_volume_by_id[houses[j]])
    
    for k in range(2, len(houses)):
        m.addConstr(total_volume_by_id[houses[k]]<=u[k])
        m.addConstr(u[k]<= 216)
    
    ##Optimize the model
    m.optimize()
    route_times[route]= obj.getValue()
print(route_times)




