"""
Created on Tue Sep 28 19:45:05 2021

@author: Emerson Rico
"""

from gurobipy import* 
import numpy as np
m = Model("Crop_Rotation")

#Importing data ---------------------------------------------------------------
coef_corn = np.loadtxt(open("M_Corn.csv", "rb"), delimiter=",")
coef_mungbean = np.loadtxt(open("M_Mungbean.csv", "rb"), delimiter=",")
coef_rice = np.loadtxt(open("M_UplandRice.csv", "rb"), delimiter=",")
coef_agriuse = np.loadtxt(open("agricultural_use.csv", "rb"), delimiter=",")

#Definition of parameters and indices =========================================
nland = 106203                          #Number of lands
nperiod = 12                            #number of period
crop = np.arange(0,3,1)                 #Crop variety dimension
T={0:6, 1:3, 2:6}                       #Period requirements
minsuit = 0.6                           #minimum suitability

#Indexing =====================================================================
period =np.arange(0,nperiod,1)          
coor = np.arange(0,nland,1)
coor2 = []
for l in coor:
    if coef_agriuse[l,2].any() == 1: coor2.append(l)

#suitability coefficients =====================================================
coef = {}
for p in period:
    for l in coor:
        coef[0,p,l] = coef_corn[l,p+2]
        coef[1,p,l] = coef_mungbean[l,p+2]
        coef[2,p,l] = coef_rice[l,p+2]
        
# Clearing imported csv data to save space ====================================
del coef_corn
del coef_mungbean
del coef_rice

#Defining variables ===========================================================

var2 = {}  #Assignment variable
var = {}   #Covering variable
for c in crop:
    for p in period:
        for l in coor:
            var[c,p,l] = m.addVar(vtype=GRB.BINARY)
        for l in coor:
            var2[c,p,l] = m.addVar(vtype=GRB.BINARY)

# Create objective ============================================================
m.setObjective(quicksum((var[c,p,l]+var2[c,p,l])*coef[c,p,l] for c in crop for p in period for l in coor), GRB.MAXIMIZE)
m.update()

#System Constraints ===========================================================

# Assignment constraints
for l in coor2:
    for p in period:
            m.addConstr((quicksum(var[c,p,l]+var2[c,p,l] for c in crop))<=1)

#Time constraints
for l in coor2:
    for p in period:
        for c in crop:
            m.addConstr((var2[c,p,l]*(T[c]-1))-(quicksum(var[c,(p+q)%nperiod,l] for q in np.arange(1,T[c],1)))<=0)


#Avoid intersection of covering and covering wihtout planting
for l in coor2:
    for c in crop:
         m.addConstr((quicksum(var[c,p,l]-(var2[c,p,l]*(T[c]-1)) for p in period))==0)

#non-agricultural area 
for l in coor:
    if (coef_agriuse[l,2]).any() == 0:
        m.addConstr((quicksum(var[c,p,l]+var2[c,p,l] for c in crop for p in period))==0)

#minimum suitability requirement
for p in period:
    for c in crop:
        for l in coor2:
            if coef[c,p,l] < minsuit:
                m.addConstr(var[c,p,l]+var2[c,p,l]==0)
         
m. optimize()