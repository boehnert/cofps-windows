
# ---------------------------------------------------------------------------
#
# ---------------------------------------------------------------------------


import arcpy, os, gc, sys, traceback, glob, subprocess, os

from arcpy import env
from arcpy.sa import *
import HRRR_images
import HRRR_Winds
import HRRR_WindsZoom2
import HRRR_aviation
import HRRR_Windimages
import logHRRR
import readTimes
import cofps_webService



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
varList = ["TT_2m_F","RH","Wind_Gust","Wind_Zoom0","Wind_Zoom1","Wind_Zoom2"]

    
def main(logFile):
    try:
        
        statement = "HRRR_atm.py is called "
        print statement
        logHRRR.main(logFile,statement)
        #call HRRR_Winds in order to convert the winds to shapefiles and to generate new resolutions
        statement = "Converting Winds "
        print statement
        logHRRR.main(logFile,statement)
        HRRR_Winds.main(shapeWindDir,dataDir,mxdOutput)
        statement = "Finished converting Winds "
        print statement
        logHRRR.main(logFile,statement)
        #lines = read_txt(logfile)
        lines = readTimes.read_time_txt()

        #run again to convert native
        print "Working on Zoom2"
        HRRR_WindsZoom2.main(shapeWindDir,dataDir,mxdOutput)
        print "----Done with Zoom2---"

        
        for v in varList:
            statement = "Working on variable " + v
            print statement
            logHRRR.main(logFile,statement)
            
            if v == "Wind_Zoom0":
                varName = "Wind Zoom Out"
                templateMap =os.path.join(mxdDir, "HRRR_Wind_Zoom0template.mxd")
                mxdcopy = os.path.join(mxdOutput, "HRRR_Wind_Zoom0.mxd")
                dataInput = os.path.join(shapeWindDir,"S_D_0_")
                layerFile = os.path.join(layerDir, "wind.lyr")
                extension = ".shp"
            elif v == "Wind_Zoom1":
                varName = "Wind Zoom In"
                templateMap =os.path.join(mxdDir, "HRRR_Wind_Zoom1template.mxd")
                mxdcopy = os.path.join(mxdOutput, "HRRR_Wind_Zoom1.mxd")
                dataInput = os.path.join(shapeWindDir,"S_D_1_")
                layerFile = os.path.join(layerDir, "wind.lyr")
                extension = ".shp"
            elif v == "Wind_Zoom2":
                varName = "Wind Zoom In"
                templateMap =os.path.join(mxdDir, "HRRR_Wind_Zoom2template.mxd")
                mxdcopy = os.path.join(mxdOutput, "HRRR_Wind_Zoom2.mxd")
                dataInput = os.path.join(shapeWindDir,"S_D_2_")
                layerFile = os.path.join(layerDir, "wind.lyr")
                extension = ".shp"
            elif v == "Wind_Gust":
                varName = "Wind Gust "
                templateMap =os.path.join(mxdDir, "HRRR_Wind_Gusttemplate.mxd")
                mxdcopy = os.path.join(mxdOutput, "HRRR_Wind_Gust.mxd")
                dataInput = os.path.join(shapeWindDir,"web_GUST_MPH_")
                layerFile = os.path.join(layerDir, "gust.lyr")
                extension = ".tif"
            elif v == "TT_2m_F":
                varName = "Temperature "
                templateMap =os.path.join(mxdDir, "HRRR_Temperaturetemplate.mxd")
                mxdcopy = os.path.join(mxdOutput, "HRRR_Temperature.mxd")
                dataInput = os.path.join(shapeWindDir,"web_TT_2m_F_")
                layerFile = os.path.join(layerDir, "T2F.lyr")
                extension = ".tif"
            elif v == "RH":
                varName = "Relative Humidity "
                templateMap =os.path.join(mxdDir, "HRRR_RHtemplate.mxd") 
                mxdcopy = os.path.join(mxdOutput, "HRRR_RH.mxd")
                dataInput = os.path.join(shapeWindDir,"web_RH_")
                layerFile = os.path.join(layerDir, "RH.lyr")
                extension = ".tif"
           
            statement = "create map service for " + varName
            logHRRR.main(logFile,statement)
            HRRR_images.main(lines,templateMap,dataInput,layerFile,mxdcopy,varName,extension,v,logFile)
            statement = "Finished making map service for " + varName
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
    logFile = args[1]
    
    
    main(logFile)
   
   





