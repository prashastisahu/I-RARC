"""
Created on Wed January 16 2024 - 14:25

@author: Prashasti Sahu & Malek Bekiri
-------------------------------------------------------------------------

Reads data for a I-RARC, builds the model, and solves it.
Then it also creates different output files. 

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

def main():
    return

def IRARC():
    return

def writeresults():
    return

def writeexcelfile():
    return

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
    
    ##############################################################################
    
    #                     Read input data 
    
    ##############################################################################
    
  
   
    # Parameters and Sets
    CE_nl = pd.read_excel(data, sheet_name='IRARC' , usecols= ['Pre-config demands per link'])  #set of existing connections per link 
    CAll_nl = pd.read_excel(data, sheet_name='IRARC' , usecols= ['Post-config demands per link']) #set of existing and new connections per link 
    CBc = pd.read_excel(data, sheet_name='No of tributory slots required' , usecols= ['CBc'])  #number of slots required by a connection c
    NL = pd.read_excel(data, sheet_name='Links' , usecols= ['IP links E']) #Network Links: Represents all links in the network
         
    
    CE = CAll_nl.loc['d1':'d59', :] # Existing Connections: All connections present before reconfiguration 
    CAll = CAll_nl.loc['d1':'d66', :] #Total Connections: Includes 𝐶𝐸 and newly added connections.
    
    # Extract unique values from the 'IP links E' column
    unique_NL = NL['IP links E'].unique()

    NBnl = 32 #The total number of slots in a network link 𝑛�
    M = 1000 #A large constant number
    m = 0.0001 #A small constant number


    ######################################## Variables ##############################################
    
    # 1.d𝑖𝑠𝑐𝑖(𝑐𝑖 ∈ 𝐶𝐸): A binary variable that indicates if an existing connection must be disrupted for completing the reconfiguration.
    #   Binary variable indicating if an existing connection must be disrupted.
    #   Total number of this variable is equal to the number of connections in set C_E.
    #   Create variable names for each existing connection in the form "disc0", "disc1", ..., "disc(len(CE)-1)"
    varnames_disc = ["disc" + str(i) for i in range(len(CE))]
    # Add binary variables to the CPLEX model
    disc = list(c.variables.add(
                            obj=0,  # Objective coefficient (could be set to 0 since it's a binary decision)
                            lb=[0] * len(CE),  # Lower bound (0 for binary)
                            ub=[1] * len(CE),  # Upper bound (1 for binary)
                            types=[c.variables.type.binary] * len(CE),  # Type (binary)
                            names=varnames_disc
                            ))



    # 2.𝑒𝑐𝑖,𝑐𝑗(𝑐𝑖 ∈ 𝐶𝐸, 𝑐𝑗 ∈ 𝐶𝐴𝐿𝐿, 𝑐𝑖 ≠ 𝑐𝑗): A binary variable that indicates whether there is an edge from connection 𝑐𝑗 to connection 𝑐𝑖
    #   in the resulting RDD.
    # Create variable names for each pair of connections in the form "edge01", "edge02", ..., "edge(N_connections-1)(N_connections-2)"
    varnames_edges = ["e" + "c" + str(i) + "c" + str(j) for i in range(len(CE)) for j in range(len(CAll)) if i != j]
    # Add binary variables to the CPLEX model
    edges = list(c.variables.add(
                            obj=0,  # Objective coefficient (could be set to 0 since it's a binary decision)
                            lb=[0] * len(varnames_edges),  # Lower bound (0 for binary)
                            ub=[1] * len(varnames_edges),  # Upper bound (1 for binary)
                            types=[c.variables.type.binary] * len(varnames_edges),  # Type (binary)
                            names=varnames_edges
                            ))
    

    # 3. rs𝑐𝑖,𝑐𝑗𝑛𝑙 (𝑛𝑙 ∈ 𝑁𝐿, 𝑐𝑖 ∈ 𝐶𝐸, 𝑐𝑗 ∈ 𝐶𝐴𝐿𝐿 ): An integer variable that indicates the number of slots assigned to 𝑐𝑗 after reconfiguration from the 
    # slots that are occupied by 𝑐𝑖 before reconfiguration in a network link 𝑛𝑙.
    # Create variable names for each triple (connection, connection, network link)
    varnames_rs = ["rs" + "c" + str(i) + "c" + str(j) + "nl" + str(nl) for i in range(len(CAll)) for j in range(len(CAll)) for nl in unique_NL]
    # Add integer variables to the CPLEX model
    rs = list(c.variables.add(
                        obj=0,  # Objective coefficient (could be set to 0 since it's an integer decision)
                        lb=[0] * len(varnames_rs),  # Lower bound (0 for integer)
                        ub=[cplex.infinity] * len(varnames_rs),  # Upper bound (could be set to a suitable upper limit)
                        types=[c.variables.type.integer] * len(varnames_rs),  # Type (integer)
                        names=varnames_rs
                        ))
    
    
    # 4. rs𝑐𝑗𝑛𝑙(𝑛𝑙 ∈ 𝑁𝐿, 𝑐𝑗 ∈ 𝐶𝐴𝐿𝐿𝑛𝑙 ): An integer variable that indicates the number of slots assigned to 𝑐𝑗 after reconfiguration among the 
    # slots that are unoccupied by any connection before configuration in a network link 𝑛𝑙.
    # Create variable names for each pair (connection, network link)
    varnames_ns = ["ns" + "c" + str(j) + "nl" + str(nl) for j in range(len(CAll)) for nl in NL]
    # Add integer variables to the CPLEX model
    ns = list(c.variables.add(
                        obj=0,  # Objective coefficient (could be set to 0 since it's an integer decision)
                        lb=[0] * len(varnames_ns),  # Lower bound (0 for integer)
                        ub=[cplex.infinity] * len(varnames_ns),  # Upper bound (could be set to a suitable upper limit)
                        types=[c.variables.type.integer] * len(varnames_ns),  # Type (integer)
                        names=varnames_ns
                        ))



    












    # Access the values of the binary variables
    for i in range(len(CE)):
        print(f"{varnames_disc[i]}: {disc[i].solution_value}")

    # Access the values of the binary variables
    for name, edge in zip(varnames_edges, edges):
        print(f"{name}: {edge.solution_value}")
    return