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
    C_E_nl = pd.read_excel(data, sheet_name='IRARC' , usecols= ['Pre-config demands per link'])  #set of demands/connections per link pre-configuration
    C_All_nl = pd.read_excel(data, sheet_name='IRARC' , usecols= ['Post-config demands per link']) #set of demands/connections per link post-configuration
    CBc = pd.read_excel(data, sheet_name='No of tributory slots required' , usecols= ['CBc'])  #number of slots required by a connection c
    NL = pd.read_excel(data, sheet_name='Links' , usecols= ['IP links E']) #Network Links: Represents all links in the network
         
    # Extracting rows d1 to d59 into DataFrame CE
    C_E = C_All_nl.loc['d1':'d59', :]

    # Extracting rows d1 to d66 into DataFrame CF
    C_All = C_All_nl.loc['d1':'d66', :]

    #Decision Variables




    return