"""
Created on Wed January 16 2024 - 14:25

@author: Prashasti Sahu & Malek Bekiri
-------------------------------------------------------------------------

This code reads data for an I-RARC model, builds the model, and generated the output. 

Input data:
    
CE: Existing Connections: All connections present before reconfiguration.
CAll: Total Connections: Includes CE and newly added connections.
NL: Network Links: Represents all links in the network.
CE_nl: Pre-Reconfiguration Connections: Subset of CE in each network link before changes.
CAll_nl: Post-Reconfiguration Connections: Includes new and existing connections in each link.
CBc: The number of slots required by a connection c (c ∈ CAll). 
NB_nl: The total number of slots in a network link nl.
M: A large constant number, e.g. 10000.
m: A small constant number, e.g. 0.0001.

Modeling variables:
1. disci(ci ∈ CE): A binary variable that indicates if an existing connection must be disrupted for completing the 
reconfiguration.
2. 𝑒𝑐𝑖,𝑐𝑗(𝑐𝑖 ∈ 𝐶𝐸, 𝑐𝑗 ∈ 𝐶𝐴𝐿𝐿, 𝑐𝑖 ≠ 𝑐𝑗)A binary variable that indicates whether there is an edge from connection 𝑐𝑗
to connection 𝑐𝑖 in the resulting RDD.
3. 𝑟𝑠𝑐𝑖,𝑐𝑗𝑛𝑙 (𝑛𝑙 ∈ 𝑁𝐿, 𝑐𝑖 ∈ 𝐶𝐸, 𝑐𝑗 ∈ 𝐶𝐴𝐿𝐿 )An integer variable that indicates the number of slots assigned to 𝑐𝑗 after reconfiguration from the 
slots that are occupied by 𝑐𝑖 before reconfiguration in a network link 𝑛𝑙.
4. 𝑛𝑠𝑐𝑗𝑛𝑙(𝑛𝑙 ∈ 𝑁𝐿, 𝑐𝑗 ∈ 𝐶𝐴𝐿𝐿𝑛𝑙 )An integer variable that indicates the number of slots assigned to 𝑐𝑗 after reconfiguration among the 
slots that are unoccupied by any connection before configuration in a network link 𝑛𝑙.


Objective:
minimize sum(ci ∈ CE) disci + m * sum (ci ∈ CE, cj i ∈ CAll, ci = cj  ) e(ci,cj)

Constraints:
Type 1:     forall IP links e ∈ E: sum(d ∈ D) sum(p ∈ p(d)) xdp0 <= Ye0*uc
Type 2:     forall demands d ∈ D, forall states s ∈ S : sum(p ∈ p(d)) xdps >= h(d)
Type 3:     forall states s ∈ S, forall demands d ∈ D, forall paths p ∈ p(d): xdps = xdp0 - sum(e ∈ E(d,p)) B(e,s) * zdpe
Type 4:     forall demands d ∈ D, forall paths p ∈ p(d), forall states s ∈ S:  xdps <= xdp0
Type 5:     forall IP links e ∈ E:  Ye0 >= 0
Type 6:     forall demands d ∈ D, forall paths p ∈ p(d): xdp0 >= 0
Type 7:     forall demands d ∈ D, forall paths p ∈ p(d), forall states s ∈ S:  xdps >= 0 
Type 8:     forall demands d ∈ D, forall paths p ∈ p(d), forall states s ∈ S:  zdpe >= 0



"""
from __future__ import print_function

import pandas as pd

import cplex
from tqdm import tqdm
import os.path
from openpyxl import Workbook
import openpyxl
import numpy as np

def Path():
    return

def main():
    return

def IRARC():
    c, var_type1, var_type2, var_type3, var_type4, CBc, CE, CAll, NL = configureproblem(data)
    c.solve()

    return

def writeresults():
    return

def writeexcelfile(c, var_type1, var_type2, var_type3, var_type4, CBc, CE, CAll, NL):
    solution = c.solution

    #################################################
    
    #                   Print Objective
    
    #################################################
    
    # Print te objective value
    print("Objective value = ", solution.get_objective_value())
    print()
    
    #################################################
    
    #                   Print Variables
    
    #################################################
    
    
    # num_of_variables gets the total number of variables
    num_of_variables = c.variables.get_num()
    
    print("Total number of variables is =  %d " % (num_of_variables))
    print()
    print()

    
    # prints the variables of type 1 with their corresponding values
    var_names = c.variables.get_names()
    
    #uncomment this part if you want to print the variables and constraints in the screen
    # '''
    # x = solution.get_values(var_type1)
    # for j, val in enumerate(x):
    #     print("%d Variable {0} = %17.10g".format(var_names[j]) % (j+1, val))
    # print()



def configureproblem(data):


    ##############################################################################
    
    #                   create a CPLEX object 
    
    ##############################################################################

    c = cplex.Cplex()
    
    #tolerance setting for the optimization problem
    CPLX_LP_PARAMETERS = {
    'simplex.tolerances.optimality' : 1e-9,
    'simplex.tolerances.feasibility' : 1e-9,
    'simplex.tolerances.gap' : 2e-4
    } 

    c.parameters.simplex.tolerances.optimality.set(CPLX_LP_PARAMETERS['simplex.tolerances.optimality'])
    c.parameters.simplex.tolerances.feasibility.set(CPLX_LP_PARAMETERS['simplex.tolerances.feasibility'])
    
    ########################################################################################################
    
    #                                      Read input data 
    
    #########################################################################################################
  
    CE = pd.read_excel(data, sheet_name='Links' , usecols= ['Pre-config connections per  link'])  #set of existing connections per link 
    CAll = pd.read_excel(data, sheet_name='Links' , usecols= ['Post-config connections per link']) #set of existing and new connections per link 
    CBc = pd.read_excel(data, sheet_name='Connections' , usecols= ['No of slots required'])  #number of slots required by a connection c
    NL = pd.read_excel(data, sheet_name='Links' , usecols= ['IP links (nl)']) #Network Links: Represents all links in the network
            

    # CE = CAll_nl.loc[0:58] # Existing Connections: All connections present before reconfiguration 
    # CAll = CAll_nl.loc[:] #Total Connections: Includes 𝐶𝐸 and newly added connections.
   
    # print(CAll)


    NBnl = 32 #The total number of slots in a network link 𝑛l
    M = 1000 #A large constant number
    m = 0.0001 #A small constant number


    #######################################################################################################

    #                                     Add variables
    
    ########################################################################################################
    
    # 1.d𝑖𝑠𝑐𝑖(𝑐𝑖 ∈ 𝐶𝐸): Binary variable indicating if an existing connection must be disrupted.
    #   Total number of this variable is equal to the number of connections in set CE for a particular link.
    #   Variable names for each existing connection is in the form "disc0", "disc1", ..., "disc(len(CE)-1)"
    varnames_disc = ["disc" + str(i+1) for i in range(len(CE))]
   
    var_type1 = list(c.variables.add(
                            obj=[1] * len(CE), 
                            lb=[0] * len(CE), 
                            ub=[1] * len(CE),  
                            types=['B'] * len(CE), 
                            names = varnames_disc
                            ))


    # 2.𝑒𝑐𝑖,𝑐𝑗(𝑐𝑖 ∈ 𝐶𝐸, 𝑐𝑗 ∈ 𝐶𝐴𝐿𝐿, 𝑐𝑖 ≠ 𝑐𝑗): A binary variable that indicates whether there is an edge from connection 𝑐𝑗 to connection 𝑐𝑖
    # in the resulting RDD where 0≤i<len(CE) and 0≤j<len(CAll).
    # Variable names for each pair of connections is in the form "ec1c2", "ec1c3", ..., "ec(len(CE)-1)c(len(CAll)-1)"
    varnames_edges = ["e" + "c" + str(i+1) + "c" + str(j+1) for i in range(len(CE)) for j in range(len(CAll)) if i != j]

    var_type2 = list(c.variables.add(
                            obj=[m] * len(varnames_edges),  
                            lb=[0] * len(varnames_edges),  
                            ub=[1] * len(varnames_edges),  
                            types=['B'] * len(varnames_edges), 
                            names = varnames_edges
                            ))
    

    # 3. rs𝑐𝑖,𝑐𝑗𝑛𝑙 (𝑛𝑙 ∈ 𝑁𝐿, 𝑐𝑖 ∈ 𝐶𝐸, 𝑐𝑗 ∈ 𝐶𝐴𝐿𝐿 ): An integer variable that indicates the number of slots assigned to 𝑐𝑗 after reconfiguration from the 
    # slots that are occupied by 𝑐𝑖 before reconfiguration in a network link 𝑛𝑙.
    # Variable names for each assignment of number of slots between ci and cj.
    varnames_rs = ["rs" + "c" + str(i+1) + "c" + str(j+1) + "nl" + str(nl) for i in range(len(CE)) for j in range(len(CAll)) for nl in NL['IP links (nl)']]

    var_type3 = list(c.variables.add(
                        obj=[0] * len(varnames_rs),  # Objective coefficient 
                        lb=[0] * len(varnames_rs),  # Lower bound (0 for integer)
                        ub=[cplex.infinity] * len(varnames_rs),  # Upper bound (could be set to a suitable upper limit)
                        types=['I'] * len(varnames_rs),  # Type (integer)
                        names=varnames_rs
                        ))
    
    
    # 4. rs𝑐𝑗𝑛𝑙(𝑛𝑙 ∈ 𝑁𝐿, 𝑐𝑗 ∈ 𝐶𝐴𝐿𝐿𝑛𝑙 ): An integer variable that indicates the number of slots assigned to 𝑐𝑗 after reconfiguration among the 
    # slots that are unoccupied by any connection before configuration in a network link 𝑛𝑙.
    # Create variable names for each pair (connection, network link)
    varnames_ns = ["ns" + "c" + str(j+1) + "nl" + str(nl) for j in range(len(CAll)) for nl in NL['IP links (nl)']]
    # Add integer variables to the CPLEX model
    var_type4 = list(c.variables.add(
                        obj=[0] * len(varnames_ns),  # Objective coefficient (could be set to 0 since it's an integer decision)
                        lb=[0] * len(varnames_ns),  # Lower bound (0 for integer)
                        ub=[cplex.infinity] * len(varnames_ns),  # Upper bound (could be set to a suitable upper limit)
                        types=["I"] * len(varnames_ns),  # Type (integer)
                        names=varnames_ns
                        ))
    
    # 5. New variable: xci,k,nl : A binary  variable indictaing if slot k is assigned to connection ci on network nl.
    

    ##################################################################################################################
    
    #                                           Add Objective 
    
    ##################################################################################################################
    
    # Set the objective function coefficients
    # c.objective.set_linear(list(zip( , )))



    ###################################################################################################################
    
    #                                           Constraints 

    ###################################################################################################################

    # Remarks: All constraints for IRARC problem formulation are linear constraints.    
    # To add constraints with cplex we need these arguments: 
    #1. lin_expr - is a matrix in list-of-lists format. lin_expr contains ind and val as arguments.
    #   ind - here we specify the variable type that is needed for the current constraint. Because CPLEX assigns unique index to 
    #   variables, we can access then using these indexes.
    #   val - here we specify the coefficients in front of variable indicies
    #2. senses - specifies the senses of the linear constraint. We use these types:
    #   - L for less-than
    #   - G for greater-than
    #   - E for equal
    #3. rhs - is the right hand side of the equation. Most of the time rhs is a list of zeros since the variables that are on the right
    #   hand side of the equation, we can bring them to the left hand side of the equation.
    #5. names (optional) - specifies the names of constraints.


    # 1. Constraint of type 1: Constraint (eq 3) ensures that, in a network link ݈݊, the required number of slots by a connection
    # cj after reconfiguration (CBcj) is equal to the total number of slots assigned to ܿcj, which includes the slots occupied by any 
    # connection before reconfiguration (∑ rs𝑐𝑗𝑛𝑙(𝑛𝑙 ∈ 𝑁𝐿, 𝑐𝑗 ∈ 𝐶𝐴𝐿𝐿𝑛𝑙 )) for  and the slots unoccupied before reconfiguration (݊nscjnl). 
    # Iterate over each connection and network link
    for nl in NL['IP links (nl)']:
        for j in range(len(CAll)):
            # Constraint for Type 1 ∑ rs𝑐𝑗𝑛𝑙(𝑛𝑙 ∈ 𝑁𝐿, 𝑐𝑗 ∈ 𝐶𝐴𝐿𝐿𝑛𝑙 ) + ݊nscjnl = CBc[j]
            
            #Constraint for Type 3 & 4 variable
            ind = [var_type3[i+1] for i in range(len(CE))] + [var_type4[j]]
                        
            # val gives the coefficients of the indicies, length of the list of ones is the same as the length of listOfNumbers.
            val = [1] * (len(CE) * len(CAll) * len(NL['IP links (nl)'])) + [1] * (len(CAll) * len(NL['IP links (nl)']))
            
            # lin_expr is a matrix in list-of-lists format. The first sub-list contains the list of indices (ind) and the second sub-list contains the list of coefficients (val)
            exp = [[ind, val]]       
            
            # Add a constraint for each network link and connection
            c.linear_constraints.add(
                                lin_expr= exp,
                                senses=['E'],  # 'E' for equality
                                rhs=[CBc.iloc[j]],  # Right-hand side of the constraint
                                names=['constraint(eq3)' + str(j) + '_' + str(nl)]  # Constraint name
                                )

   


    # # 2. Constraint of type 2: Constraint (eq 4) ensures that, in a network link݈, the total number of slots that are occupied by an 
    # # existing connection ci before reconfiguration and are also assigned to other connections after reconfiguration must not exceed 
    # # the required number of slots of ci.
    for nl in NL['IP links (nl)']:
        for i in range(len(CE)):
            # Constraint for Type 3 variable
            ind = [var_type3[j] for j in range(len(CAll)) if j != i]
            
            # val gives the coefficients of the indicies.
            val = [1] * len(ind)

            # lin_expr is a matrix in list-of-lists format.
            exp = [[ind, val]]

            c.linear_constraints.add(
                lin_expr= exp,
                senses= ['L'],
                rhs=[CBc.iloc[i]],  # Right-hand side of the constraint
                names=['constraint(eq4)' + str(i) + '_' + str(nl)]  # Constraint name
            )
    

    # 3. Constraint of type 3: Constraint (eq 5) ensures that, in a network link ݈݊, the total number of slots that are unoccupied before reconfiguration 
    # and are assigned to connections after reconfiguration should not exceed the total number of slots that are unoccupied before 
    # reconfiguration.
    for nl in NL['IP links (nl)']:
            # Constraint for Type 3 variable
            ind = [var_type4[j] for j in range(len(CAll))] +  [CBc.iloc[i] for i in range(len(CE))] 
            
            # val gives the coefficients of the indicies.
            val=[1] * len(ind)

            # lin_expr is a matrix in list-of-lists format.
            exp = [[ind, val]]

            c.linear_constraints.add(
                lin_expr= exp,
                senses= ['L'],
                rhs= [NBnl],
                names= ['constraint(eq5)' + str(i) + '_' + str(j)]
            )


    # 4. Constraint of type 4: Constraint (eq 6) ensures that if at least one slot occupied by a connection ܿci before reconfiguration is 
    # assigned to a connection ܿcj after reconfiguration in any network link, then ݁e(ci,cj) must be 1.
    for j in range(len(CAll)):
            for i in range(len(CE)):
                if i != j:
                    # Constraint for Type 3 variable
                    ind=[var_type2[i]] +  [var_type3[i,j]] 
            
                    val=[1, -M ]

                    exp = [[ind, val]]

                    c.linear_constraints.add(
                        lin_expr= exp,
                        senses= ['L'],
                        rhs= [0],
                        names= ['constraint(6)_c{}_c{}'.format(i,j)]
                    )

    # 5. Constraint 5: Doubt
                    
    # 6. New Constraint: Contiguity constraint ensures that if two slots k and k+1 are assigned to the same connection ci on network link nl, there cannot be a slot k` such that k < K` < k+1 which is not assigned to ci. 
    # 

    


    return c, var_type1, var_type2, var_type3, var_type4, CE, CAll, CBc, NL


