
# ---------------------------------------------------------------------------
#
# ---------------------------------------------------------------------------

# --- Import system modules --- #
import sys
sys.dont_write_bytecode = True
import os
import traceback
import time
import cofps_webService
from shutil import copyfile
import glob
import logHRRR

# Import ArcGIS modules and environments
import arcpy
arcpy.env.overwriteOutput = True                                                # Module configurations
# --- End Import system modules --- #


def getName(timeStep,t):
    try:
        names =[]
        pTime = timeStep.split(",")[1]
        if t < 10 :
            p = "0"+ str(t)
        else:
            p = str(t)
        name = "Time %s %s" %(p,pTime)
        
        return name            
        
    except Exception as e:
        print e

def getP(timeStep,t):
    try:
        names =[]
        pTime = timeStep.split(",")[1]
        
        if t < 10 :
            p = "0"+ str(t)
        else:
            p = str(t)
        name = "Time %s %s" %(p,pTime)
        
        return p            
        
    except Exception as e:
        print e
       
