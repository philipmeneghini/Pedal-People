#!/usr/bin/env python
# coding: utf-8

# In[ ]:


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

""" FINDING TOTAL COLLECTION AMOUNTS """

trash_vol = trash_frame.trash
paper_vol = trash_frame.paper
container_vol = trash_frame.containers
compost_vol = trash_frame.compost

total_volume_by_id = {}

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
index_to_id = {}
count =  0

for id in ids:
    id_to_index[str(id)] = count
    index_to_id[count] = id 
    count += 1

route_times = {}

##If there are 39 routes we store all the time values for a route in the following array
m=gp.Model()
    
##All the houses in a route given by the index in the matrix of the values for distance, elevation and so on above
houses = 985

    ##Variables
x = m.addVars(houses, houses, vtype=GRB.BINARY, name = "x")
r = m.addVar(vtype = GRB.INTEGER)
u = m.addVars(houses, vtype=GRB.INTEGER)
    
obj=0
for i in range(0,houses):
    for j in range(0,houses):
        obj+= t[i][j]*x[i,j]
m.setObjective(obj, GRB.MINIMIZE)
    
    
    ##Constraints
    
    ##For each house there is a path in and out
    ##We start at 2 because we do not want to include collection centers
    ##Outgoing
m.addConstrs((gp.quicksum(x[i,j]for j in range(0, houses))==1 for i in range(0, houses-2)))

    #res1=np.zeros(len(houses)-2)
    #for i in  range(2, len(houses)):
        #res1[i-2]=0
        #for j in range(0, len(houses)):
            #res1[i]+= float(x[i,j])
        #m.addConstr(res1[i]==1)
        
    ##Ingoing
    #res2=np.zeros(len(houses))
    #for i in range(2, len(houses)):
        #for j in range(0, len(houses)):
            #res2[i]+= x[j,i]
        #m.addConstr(res2[i]=1)
m.addConstrs((gp.quicksum(x[j,i] for j in range(0, houses))==1 for i in range(0, houses-2)))
    ##Constraint for how many edges we can have leaving and entering the collection centers
res4=0
res5=0
for i in range(0,houses-2):
    res4+=x[983,i]
    res4+=x[984,i]
    res5+=x[i,983]
    res5+=x[i,984]
m.addConstr(res4==r)
m.addConstr(res5==r)
    
    ##We need a constraint saying that there must be at least one run
m.addConstr(r>=1)
    
    ##Constraint saying a bike cannot go from one house to the same house
for i in range(0, houses):
    for j in range(0, houses):
        if (i ==j):
            m.addConstr(x[i,j]==0)
    ##We set up the constraint to make sure each run goes to a collection center and a bike does not get overly full 216 gallons
for i in range(0,houses-2):
    for j in range(0, houses-2):
        if j !=i:
            m.addConstr(u[j]-u[i] + 216*(1-x[i,j])>= total_volume_by_id[index_to_id[j]])
    
for k in range(0, houses-2):
    m.addConstr(total_volume_by_id[index_to_id[k]]<=u[k])
    m.addConstr(u[k]<= 216)
                            
                            
    ##Making it so full bikes do not go up hills greater than 3 degree incline (0.05233 radians)
    #for j in range(0, len(houses)):
        #for i in range(0,len(houses)):
            #dist = distance_arr[id_to_index[str(houses[j])]][id_to_index[str(houses[i])]]
            #elev = elevation_arr[id_to_index[str(houses[j])]][id_to_index[str(houses[i])]]
            #rad= math.atan(elev/dist)
            #if rad > 0.052359:
                #m.addConstr(u[i] == total_volume_by_id[houses[i]])
    
    ##Optimize the model
m.optimize()
for v in m.getVars():
    print(v.varName, v.x)
print('resulting time: '+ str(obj.getValue()))
    


# In[ ]:





# In[ ]:




