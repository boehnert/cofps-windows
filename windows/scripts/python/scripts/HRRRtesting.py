
# ---------------------------------------------------------------------------
# HRRR.py HRRR_atmosphere
# or
#  HRRR.py HRRR_aviationMax
# ---------------------------------------------------------------------------


import arcpy, os, gc, sys, traceback, glob, subprocess, os

from arcpy import env
from arcpy.sa import *
import HRRR_images
import HRRR_Winds
import HRRR_aviation
import HRRR_Windimages
import logHRRR
import readTimes
import cofps_webService
import HRRR_atm
import HRRR_atmtesting
import HRRR_avStart
import HRRR_avStart2



# Check out any necessary licenses
arcpy.CheckOutExtension("spatial")
arcpy.env.overwriteOutput = True


shapeWindDir = r"E:\cofireop\hrrr\gisdata"
dataDir = r"E:\cofireop\Mapping\data"
# Directory storing HRRR GIS data
mxdDir = r"E:\cofireop\Mapping\templateMaps"
mxdOutput =r"E:\cofireop\Mapping\HRRRMaps"

# Directory storing HRRR GIS Map Documents
layerDir = r"E:\cofireop\Mapping\layers"

logDir = r"E:\cofireop\HRRRlogs"
varList = ["TT_2m_F","RH","Wind_Gust"]


def createLog(fileName) :
    
    writeFile = os.path.join(logDir,fileName)
    f= open(writeFile,"wb+")
    
    f.close()

    return(writeFile)
        
    
def main(script):
    try:
        tic = str(time.strftime("%d_%m_%Y_%H_%M_%S"))
        fileName = script +"_" +tic +".txt"
        logFile = createLog(fileName)
        statement = "HRRR.py is called "
        print statement
        logHRRR.main(logFile,statement)
        
        if (script == "HRRR_atmosphere") :
            
            HRRR_atm.main(logFile)
        elif (script == "HRRR_aviationMax") :
            HRRR_avStart.main(logFile)
        else :
            HRRR_avStart2.main(logFile)

        statement = "Everything is finished "
        print statement
        logHRRR.main(logFile,statement)
           

    except:
        print " IN HERE"
         # Get the traceback object
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]

        # Concatenate information together concerning the error into a message string
        pymsg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n" + str(sys.exc_info()[1])
        msgs = "ArcPy ERRORS:\n" + arcpy.GetMessages(2) + "\n"

        # Return python error messages for use in script tool or Python Window
        arcpy.AddError(pymsg)
        arcpy.AddError(msgs)

        # Print Python error messages for use in Python / Python Window
        print pymsg + "\n"
        print msgs




    # Local variables:
if __name__ == '__main__':
   
    args = sys.argv
    
    script = args[1]
    
    main(script)






