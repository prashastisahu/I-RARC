# I-RARC
ILP-based Resource Assignment and RDD Construction.

Objective: Implement the I-RARC.
• Implementation:
• This Python script implements and runs the I-RARC algorithm.
• The script is designed such that it can be used for any arbitrarily defined 
network topology and traffic matrix.

Input:
o OTN network topology, which includes parameters such as link costs and link 
capacities (i.e. type of HO-ODU and the type of tributary slot used).
o Traffic matrix of ODU demands and their corresponding routing and grooming.
(Note: the traffic matrix implicitly defines the bandwidths (BWs) of the LOODUs.)
o Note: the routing and grooming of LO-ODUs above is non-optimum, i.e. the 
capacity is not efficiently utilized, and thus, future traffic demand requests may 
get blocked.
o The input above can be for instance be defined in an excel file.

Output:
o The I-RARC calculates the optimum routing and grooming of LO-ODUs and 
the migration strategy needed to reconfigure the LO-ODUs into their optimized 
grooming and routing. This output has to be delivered as an excel file. Notice 
that this output corresponds to the optimum decision variables calculated after 
solving the I-RARC.
o The calculation of the output implies the following steps:
• Step 1: Determine globally-optimized routes
• Input: sub-optimum routing of ODU demands.
• Method: Apply conventional ILP-based routing algorithms. Note: 
this step is not solved by the I-RARC!
• Step 2: Perform resource assignment and RDD construction
• Input: sub-optimum routing and grooming of ODU demands.
• Method: Apply the I-RARC to optimize the migration strategy that 
minimizes the number of disruptions.
• Step 3: Determine the order of connection migrations
• Input: decision variables optimized by the I-RARC.
• Method: the decision variables are post-processed as to determine 
the order of connection migrations.

Design specifications. The I-RARC conforms to the following specifications:
o I-RARC output:
o Set of disrupted connections.
o Constructed Routing Dependency Diagram (RDD).
o Resource assignment for network links.
o I-RARC decision variables and parameters (i.e. constant values).
o Objective Function:To Minimize the number of connections disrupted during migration.
