
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


# Import ArcGIS modules and environments
import arcpy
arcpy.env.overwriteOutput = True                                                # Module configurations
# --- End Import system modules --- #

# --- Global Variables --- #

# Data and Map Directories
inputDir = r"E:\cofireop\hrrr\gisdata"

#input log file with times
logfile = os.path.join(inputDir, "HRRR_current_readme.log")                      # HRRR Product Generation Log file

# --- End Global Variables --- #

# --- Main codeblock --- #
def read_time_txt():
    '''Function to read the contents of the HRRR Readme file, which contains the
    times of each forecast hour.'''
    fo = open(logfile, "r")
    lines = fo.readlines()
    fo.close()
    return lines
