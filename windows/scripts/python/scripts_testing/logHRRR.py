
# ---------------------------------------------------------------------------
#
# ---------------------------------------------------------------------------

# --- Import system modules --- #
import sys
sys.dont_write_bytecode = True
import os
import traceback
import time
from shutil import copyfile
import glob
import cPickle
import pickle
import datetime as dt
from datetime import datetime




# Import ArcGIS modules and environments
import arcpy
arcpy.env.overwriteOutput = True                                                # Module configurations
# --- End Import system modules --- #

# --- Global Variables --- #


# --- End Global Variables --- #

# --- Main codeblock --- #

def main(writeFile,statement):
    try:
        start = time.ctime()
        tic = str(time.strftime("%d_%m_%Y_%H_%M_%S"))
        print start
        print tic
        
        
        f = open(writeFile,"a")
        f.write(start)
        f.write (" - ")
        f.write(statement)
        f.write("\n")
        f.close()
        
        #print 'Time elapsed: %s seconds' %(time.time()-tic)
    except Exception as e:
        print e
        print " IN HERE"
        ##         # Get the traceback object
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
        ##
        ##        # Concatenate information together concerning the error into a message string
        pymsg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n" + str(sys.exc_info()[1])
        msgs = "ArcPy ERRORS:\n" + arcpy.GetMessages(2) + "\n"
        ##
        ##        # Return python error messages for use in script tool or Python Window
        arcpy.AddError(pymsg)
        arcpy.AddError(msgs)
        ##
        ##        # Print Python error messages for use in Python / Python Window
        print pymsg + "\n"
        print msgs

# Local variables:
if __name__ == '__main__':
    try:
        args = sys.argv
        logFile = args[1]
        statement = args[2]
        main(logFile,statement)
        

    except Exception as e:
        print e

    ##        print "ERROR Happenned"
    ##         # Get the traceback object
    ##        tb = sys.exc_info()[2]
    ##        tbinfo = traceback.format_tb(tb)[0]
    ##
    ##        # Concatenate information together concerning the error into a message string
    ##        pymsg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n" + str(sys.exc_info()[1])
    ##        msgs = "ArcPy ERRORS:\n" + arcpy.GetMessages(2) + "\n"
    ##
    ##        # Return python error messages for use in script tool or Python Window
    ##        arcpy.AddError(pymsg)
    ##        arcpy.AddError(msgs)
    ##
    ##        # Print Python error messages for use in Python / Python Window
    ##        print pymsg + "\n"
    ##        print msgs
