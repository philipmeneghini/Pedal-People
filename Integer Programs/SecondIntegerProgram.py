import gurobipy as gp
from gurobipy import GRB
import numpy as np
import scipy.linalg as spla
import pandas as pd
import itertools
from matplotlib import pyplot as plt
import string


elevation_frame = pd.read_csv(r"C:\Users\philm\Documents\456\elev_diffs_2.csv")

distance_frame = pd.read_csv(r"C:\Users\philm\Documents\456\dist_diff_2.csv")

trash_frame = pd.read_csv(r"C:\Users\philm\Documents\456\trash_list.csv")

region_frame = pd.read_csv(r"C:\Users\philm\Documents\456\region_list.csv")

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
    total_volume_by_id[id] = trash + paper + containers + compost

""" END COLLECTION AMOUNTS"""

""" CREATING TIME ARRAY """
distance_arr = np.array(distance_frame)
elevation_arr = np.array(elevation_frame)
time_per_edge_arr = distance_arr



row_count = 0
col_count = 0

for row in time_per_edge_arr:
    for col_count in range(0,985):
        if(col_count < 985) and (row_count < 985):
            time_per_edge_arr[row_count][col_count] = time_per_edge_arr[row_count][col_count]/10
    row_count += 1

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

print(routes_container_house_ids)

for route in routes_container_house_ids.keys():
    string = "Route " + str(route) + " contains customers "
    for house in routes_container_house_ids[route]:
        string = string + str(house) + " "
    print(string)


route_times = {}

id_to_index = {}

count =  0

for id in ids:
    id_to_index[str(id)] = count
    count += 1


##We put in the route_times dictionary that the first linear program outputs
route_times= {'12': 1.7021809148000004, '35': 1.7336077728, '20': 2.1416403601, '26': 1.6572176937, '314': 1.6250849624000003, '53': 2.3972998786, '204': 2.026314097, '217': 1.5034715108, '539': 1.5454558798, '25': 2.2065440311, '23': 1.1733173968, '28': 2.834142888799999, '575': 0.9564710126000001, '13': 2.0835924618, '42': 3.2935311454999994, '11': 4.027384127100001, '14': 1.4313171445000004, '8': 3.1310024910000003, '34': 2.8888936056, '377': 0.44770110179999995, '24': 1.9265534905, '15': 1.1716547854, '421': 2.4703905013000003, '207': 2.067451288299999, '178': 1.6005587046678573, '336': 1.8058888625999998, '428': 1.6426791439154358, '7': 2.7838135745, '33': 2.0608534318999996, '45': 0.038995136799999996, '37': 2.6416807599999994, '333': 1.4066867290000002, '29': 1.6538125321000001, '18': 2.3272548803, '239': 1.833294072, '4': 1.8278570911, '27': 2.6927258255, '560': 1.0309476644, '561': 1.268744278, '553': 2.3407582274, '75': 2.1832565377000006}



ids_as_ints_list = []
for id in route_times.keys():
    ids_as_ints_list.append(int(id))


route_times_df = pd.DataFrame()
route_times_df["Time"] = route_times.values()
route_times_df["RouteID"] = route_times.keys()
route_times_df["Num Customers"] = routes_container_raw_vals.values()


num_routes = len(route_times.keys())


days = region_frame.pickup_day
region_ids = region_frame.id

houses = trash_frame.region_id


houses_per_region_tally = {}

for house in houses:
    if(house in houses_per_region_tally):
        houses_per_region_tally[house] += 1
    else:
        houses_per_region_tally[house] = 1
print(houses_per_region_tally)

houses_per_day = {}

for region_id, day in zip(region_ids, days):
    customers = houses_per_region_tally[region_id]
    if(day in houses_per_day):
        houses_per_day[day] += customers
    else:
        houses_per_day[day] = customers


sum = 0
for value in houses_per_day.values():
    sum += value
day_proportions = {}
for day, values in zip(houses_per_day.keys(), houses_per_day.values()):
    day_proportions[day] = value/sum
T=0
for routes in route_times:
    T+=route_times[routes]

day_time ={}
for day in day_proportions:
    day_time[day]= day_proportions[day]*T
print(T)


m=gp.Model()

##Our variable
##First variable is a marix with out rows representing each region by each week day and columns being all the routes
##A one in a column for a row represents that that route is in the corresponding region

reg= m.addVars(5, num_routes, vtype= GRB.BINARY)
##We use x and y to have our objective function be the minimum of the absolute value of the difference between time of theoretical and calculated regions
x= m.addVars(5)
y= m.addVars(5)
##Our objective function is going to try to minimize the difference between the time of each of our regions and the best theoretical time
##According to how many workers are working on each weekday

obj=0
for i in range(0,5):
    obj+=x[i]+y[i]
    
m.setObjective(obj, GRB.MINIMIZE)

##Constraints
##Each route must be in a region
con=0
for i in range(0, 5):
    for j in range(0,num_routes):
        con = con + reg[i,j]
    
c1 = m.addConstr(con == num_routes)

sum=[0 for k in range(num_routes)]
for j in range(0,num_routes):
    for i in range(0,5):
        sum[j]= sum[j] + reg[i, j]
    m.addConstr(sum[j]==1)
        

##This sets a constraint that the differenc between computed regions and best theoretical regions must be equal to the x[i]-y[i] variable
##This will make the objective function be equal to what we want
i=0
res= [0, 0, 0, 0, 0]
for days in day_time:
    j=0
    for route in route_times:
        res[i]+=reg[i,j]*route_times[route]
        j+=1
    m.addConstr(x[i]- y[i] + res[i] - day_time[day] == 0)
    i+=1
    
##Last constraints we want to make sure that our values for x[i] and y[i] are greater than zero so we don't get any negative values in the objective function
for i in range(0,5):
    m.addConstr(x[i]>=0)
    m.addConstr(y[i]>=0)

m.optimize()
time=0
for route in route_times:
    time+=route_times[route]

print('total time: '+ str(time))
index_to_id={}
j=0
for route in route_times:
    index_to_id[j]=route
    j=j+1


regions ={}
for i in range(0,5):
    temp=list()
    for j in range(0, num_routes):
        if reg[i,j].X==1.0:
            temp.append(index_to_id[j])
    regions[i]= temp
print(regions)
print('error: '+str(obj.getValue()))






