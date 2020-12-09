	This project consisted of two integer programs. Our goal was to optimize pickup days or regions for a local waste collection company called pedal people.
The first integer program takes all the houses in each route the pedal people have (according to route id) and then runs an integer program on each of the 
routes trying to optimize runs for the pedal people. Pedal people have their employees pick up waste on bikes with small trailers. As a result each route must 
have a certain number of runs where a worker leaves from one of the two collection centers, collects waste for a couple houses and then must go back to one of the 
collection centers to empty his/her trailer. Optimizing what houses should be in which run for each of these routes according to how much waste each house usually 
produces serves as a difficult optimization problem. This problem is a mix of the traveling salesman and bin packing problem. Our first integer program solves this 
problem and outputs a dictionary data type giving the calculated optimal times for each route when we optimized the runs on the route. This serves as an input for 
our second integer program.

	The second integer program was smaller but still tricky. Now that we had optimal running times for each of the routes we needed to figure out a good way to 
organize the routes into particular regions or trash pickup days. As a result according to how many workers (approximately) pedal people had working on each day served 
as a benchmark for proportions of times we wanted assigned on each day. We found the total time to run all the routes and then multiplied that number by 
the proportion of workers working on a given day putting all these times into a list. These are the ideally perfect time assignments for each day according to how many 
people are working on a given day so we constructed another optimization problem based around minimizing the absolute value between the routes the program assigned on each 
day versus the perfect time assignment we calculated. This program when finished assigned the routes to each day that pedal people worked in the most fair way for 
each of the workers. We called each of these constructed pickup days with routes our regions.

	Finally we ran the first integer program except on all the houses that pedal people needed to service. Calulating the optimal runs served as a way to show that 
by taking away the regions and routes that the pedal people were using, a lot of time was saved. The conclusion of the project after looking at the total time with regions and 
routes versus the total time when just considering runs served as a way to encourage the pedal people to stop constructing these abstract constructs like regions and routes 
which are taking away efficiency.

	Due to some of the data used in the program when run being private secure information about pedal people's customers I cannot provide the cvs files which my 
python program gathers data from. However the code which primarily uses gurobi is provided. A more detailed report of how each integer program works is also given 
in a formal report below.