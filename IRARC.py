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
    CE_nl = pd.read_excel(data, sheet_name='IRARC' , usecols= ['Pre-config demands per link'])  
    CAll_nl = pd.read_excel(data, sheet_name='IRARC' , usecols= ['Post-config demands per link']) 
    CBc_df = pd.read_excel(data, sheet_name='No of tributory slots required' , usecols= ['CBc'])  
    NL = pd.read_excel(data, sheet_name='Links' , usecols= ['IP links E']) 
    
    # FIXED: Proper data extraction
    # CE = CAll_nl.loc['d1':'d59', :] # This indexing doesn't work as expected
    # CAll = CAll_nl.loc['d1':'d66', :] 
    
    # Assuming the data is in rows 1-59 for CE and 1-66 for CAll
    CE = list(range(59))  # Connections d1 to d59 (0-indexed as 0-58)
    CAll = list(range(66))  # Connections d1 to d66 (0-indexed as 0-65)
    
    # Extract unique values from the 'IP links E' column
    unique_NL = NL['IP links E'].unique().tolist()
    
    # FIXED: Convert CBc to a proper list/array for indexing
    CBc = CBc_df['CBc'].tolist()  # Convert to list for easier indexing

    NBnl = 32 #The total number of slots in a network link 𝑛l
    M = 1000 #A large constant number
    m = 0.0001 #A small constant number

    ######################################## Variables ##############################################
    
    # Type 1: Binary variable for connection disruption
    varnames_disc = ["disc" + str(i) for i in range(len(CE))]
    disc_indices = c.variables.add(
        obj=[1.0] * len(CE),  # Objective coefficient 
        lb=[0] * len(CE),     # Lower bound
        ub=[1] * len(CE),     # Upper bound
        types=[c.variables.type.binary] * len(CE),
        names=varnames_disc
    )

    # Type 2: Binary variable for edges between connections
    varnames_edges = []
    for i in range(len(CE)):
        for j in range(len(CAll)):
            if i != j:
                varnames_edges.append(f"e_c{i}_c{j}")
    
    edges_indices = c.variables.add(
        obj=[m] * len(varnames_edges),  # Small coefficient in objective
        lb=[0] * len(varnames_edges),
        ub=[1] * len(varnames_edges),
        types=[c.variables.type.binary] * len(varnames_edges),
        names=varnames_edges
    )

    # Type 3: Integer variable for slot reassignment
    varnames_rs = []
    for nl in unique_NL:
        for i in range(len(CE)):
            for j in range(len(CAll)):
                varnames_rs.append(f"rs_c{i}_c{j}_nl{nl}")
    
    rs_indices = c.variables.add(
        obj=[0] * len(varnames_rs),
        lb=[0] * len(varnames_rs),
        ub=[NBnl] * len(varnames_rs),  # Upper bound is number of slots
        types=[c.variables.type.integer] * len(varnames_rs),
        names=varnames_rs
    )

    # Type 4: Integer variable for new slots
    varnames_ns = []
    for nl in unique_NL:
        for j in range(len(CAll)):
            varnames_ns.append(f"ns_c{j}_nl{nl}")
    
    ns_indices = c.variables.add(
        obj=[0] * len(varnames_ns),
        lb=[0] * len(varnames_ns),
        ub=[NBnl] * len(varnames_ns),
        types=[c.variables.type.integer] * len(varnames_ns),
        names=varnames_ns
    )

    ####################################### Constraints ############################################

    # FIXED: Constraint Type 1 (Equation 3)
    # For each connection j and network link nl:
    # Sum of reassigned slots + new slots = required slots for connection j
    constraint_counter = 0
    
    for j in range(len(CAll)):
        for nl_idx, nl in enumerate(unique_NL):
            # Variables: rs variables for all existing connections i to connection j in link nl
            # plus ns variable for connection j in link nl
            ind = []
            val = []
            
            # Add rs variables: rs_ci_cj_nl for all i in CE
            for i in range(len(CE)):
                var_name = f"rs_c{i}_c{j}_nl{nl}"
                if var_name in varnames_rs:
                    var_idx = varnames_rs.index(var_name)
                    ind.append(rs_indices[var_idx])
                    val.append(1)
            
            # Add ns variable: ns_cj_nl
            var_name = f"ns_c{j}_nl{nl}"
            if var_name in varnames_ns:
                var_idx = varnames_ns.index(var_name)
                ind.append(ns_indices[var_idx])
                val.append(1)
            
            if ind:  # Only add constraint if variables exist
                c.linear_constraints.add(
                    lin_expr=[cplex.SparsePair(ind, val)],
                    senses=['E'],  # Equality
                    rhs=[CBc[j] if j < len(CBc) else 1],  # Required slots for connection j
                    names=[f'constraint_eq3_c{j}_nl{nl}']
                )
                constraint_counter += 1

    # FIXED: Constraint Type 2 (Equation 4)
    # For each existing connection i and network link nl:
    # Sum of slots from connection i assigned to all connections <= slots occupied by i
    for i in range(len(CE)):
        for nl_idx, nl in enumerate(unique_NL):
            ind = []
            val = []
            
            # Add rs variables: rs_ci_cj_nl for all j in CAll
            for j in range(len(CAll)):
                var_name = f"rs_c{i}_c{j}_nl{nl}"
                if var_name in varnames_rs:
                    var_idx = varnames_rs.index(var_name)
                    ind.append(rs_indices[var_idx])
                    val.append(1)
            
            if ind:  # Only add constraint if variables exist
                c.linear_constraints.add(
                    lin_expr=[cplex.SparsePair(ind, val)],
                    senses=['L'],  # Less than or equal
                    rhs=[CBc[i] if i < len(CBc) else 1],  # Slots occupied by connection i
                    names=[f'constraint_eq4_c{i}_nl{nl}']
                )
                constraint_counter += 1

    # FIXED: Constraint Type 3 (Equation 5)
    # For each network link nl:
    # Sum of new slots assigned <= available unoccupied slots
    for nl_idx, nl in enumerate(unique_NL):
        ind = []
        val = []
        
        # Add ns variables for all connections j
        for j in range(len(CAll)):
            var_name = f"ns_c{j}_nl{nl}"
            if var_name in varnames_ns:
                var_idx = varnames_ns.index(var_name)
                ind.append(ns_indices[var_idx])
                val.append(1)
        
        if ind:  # Only add constraint if variables exist
            # Calculate unoccupied slots = total slots - occupied slots by existing connections
            occupied_slots = sum(CBc[i] for i in range(min(len(CE), len(CBc))))
            available_slots = max(0, NBnl - occupied_slots)
            
            c.linear_constraints.add(
                lin_expr=[cplex.SparsePair(ind, val)],
                senses=['L'],  # Less than or equal
                rhs=[available_slots],
                names=[f'constraint_eq5_nl{nl}']
            )
            constraint_counter += 1

    # FIXED: Constraint Type 4 (Equation 6)
    # If slots from connection i are assigned to connection j, then edge e_ci_cj must be 1
    for i in range(len(CE)):
        for j in range(len(CAll)):
            if i != j:
                for nl_idx, nl in enumerate(unique_NL):
                    ind = []
                    val = []
                    
                    # rs variable
                    rs_var_name = f"rs_c{i}_c{j}_nl{nl}"
                    if rs_var_name in varnames_rs:
                        var_idx = varnames_rs.index(rs_var_name)
                        ind.append(rs_indices[var_idx])
                        val.append(1)
                    
                    # edge variable with negative coefficient
                    edge_var_name = f"e_c{i}_c{j}"
                    if edge_var_name in varnames_edges:
                        var_idx = varnames_edges.index(edge_var_name)
                        ind.append(edges_indices[var_idx])
                        val.append(-M)  # Large negative coefficient
                    
                    if len(ind) == 2:  # Only add if both variables exist
                        c.linear_constraints.add(
                            lin_expr=[cplex.SparsePair(ind, val)],
                            senses=['L'],  # Less than or equal
                            rhs=[0],
                            names=[f'constraint_eq6_c{i}_c{j}_nl{nl}']
                        )
                        constraint_counter += 1

    # FIXED: Constraint Type 5 (Equation 7) - AHC constraint
    # This constraint ensures proper ordering in the RDD
    # Note: This constraint needs AHC values which aren't defined in your code
    # I'll provide a placeholder structure
    
    # Placeholder AHC values (you need to define these based on your problem)
    AHC = {i: i for i in range(len(CAll))}  # Simple placeholder values
    
    for i in range(len(CE)):
        for j in range(len(CAll)):
            if i != j:
                ind = []
                val = []
                
                # Add disruption variable
                disc_var_name = f"disc{i}"
                if disc_var_name in varnames_disc:
                    var_idx = varnames_disc.index(disc_var_name)
                    ind.append(disc_indices[var_idx])
                    val.append(M)  # Large positive coefficient
                
                # Add edge variable  
                edge_var_name = f"e_c{i}_c{j}"
                if edge_var_name in varnames_edges:
                    var_idx = varnames_edges.index(edge_var_name)
                    ind.append(edges_indices[var_idx])
                    val.append(M)  # Large positive coefficient
                
                if len(ind) == 2:  # Only add if both variables exist
                    # AHC constraint: AHC[i] - AHC[j] + M*disc[i] + M*edge[i,j] >= 0
                    c.linear_constraints.add(
                        lin_expr=[cplex.SparsePair(ind, val)],
                        senses=['G'],  # Greater than or equal
                        rhs=[AHC.get(j, 0) - AHC.get(i, 0)],
                        names=[f'constraint_eq7_c{i}_c{j}']
                    )
                    constraint_counter += 1

    print(f"Total constraints added: {constraint_counter}")
    print(f"Total variables: {c.variables.get_num()}")
    
    return c
