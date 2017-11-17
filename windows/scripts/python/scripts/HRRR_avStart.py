
# ---------------------------------------------------------------------------
#
# ---------------------------------------------------------------------------


import arcpy, os, gc, sys, traceback, glob, subprocess, os

from arcpy import env
from arcpy.sa import *
import HRRR_images
import HRRR_Winds
import HRRR_aviation
import readTimes
import cofps_webService
import logHRRR



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



avvarList = ["Maximum_WW_5000_to_15000","Maximum_WW_15000_to_21000","Maximum_HShear_5000_to_15000","Maximum_HShear_15000_to_21000","Maximum_Turbulence_15000_to_21000","Maximum_Turbulence_5000_to_15000"]
#avvarList = ["Maximum_Turbulence_15000_to_21000"]

def main(logFile):
    try:
        statement = "HRRR_avStart.py is called "
        print statement
        logHRRR.main(logFile,statement)
        #call HRRR_Winds in order to convert the winds to shapefiles and to generate new resolutions
        #HRRR_Winds.main(shapeWindDir,dataDir,mxdOutput)
        #lines = read_txt(logfile)
        lines = readTimes.read_time_txt()
        extension = ".tif"
        
        for v in avvarList :
        
            if v == "Turbulence":
                mapName = "turbulenceTemplate.mxd"
                varName = "Turbulence "
                templateMap =os.path.join(mxdDir, "turbulenceTemplate.mxd") 
                mxdcopy = os.path.join(mxdOutput, "HRRR_Turbulence")
                dataInput = os.path.join(shapeWindDir,"Turbulence_Index.shp")
                layerFile = os.path.join(layerDir, "Turbulence.lyr")
            elif v == "Maximum_WW_15000_to_21000" :
                mapName = "max_updraftTemplate.mxd"
                varName = "Maximum Updrafts and Downdrafts "
                templateMap =os.path.join(mxdDir, "HRRR_max_updraftTemplate.mxd") 
                mxdcopy = os.path.join(mxdOutput, "HRRR_Max_Updraft_downdraft_15000_to_21000")
                dataInput = os.path.join(shapeWindDir,"Maximum_WW_15000_to_21000.shp")
                layerFile = os.path.join(layerDir, "Updrafts.lyr")
            elif v == "Maximum_WW_5000_to_15000" :
                mapName = "max_updraftTemplate.mxd"
                varName = "Maximum Updrafts and Downdrafts "
                templateMap =os.path.join(mxdDir, "HRRR_max_updraftTemplate.mxd") 
                mxdcopy = os.path.join(mxdOutput, "HRRR_Max_Updraft_downdraft_5000_to_15000")
                dataInput = os.path.join(shapeWindDir,"Maximum_WW_5000_to_15000.shp")
                layerFile = os.path.join(layerDir, "Updrafts.lyr")
                
            elif v == "Maximum_Turbulence_15000_to_21000":
                mapName = "turbulenceTemplate.mxd"
                varName = "Maximum Turbulence "
                templateMap =os.path.join(mxdDir, "turbulenceTemplate.mxd") 
                mxdcopy = os.path.join(mxdOutput, "HRRR_Maximum_Turbulence_15000_to_21000")
                dataInput = os.path.join(shapeWindDir,"Maximum_Turbulence_15000_to_21000.shp")
                layerFile = os.path.join(layerDir, "Turbulence.lyr")
            elif v == "Maximum_HShear_5000_to_15000":
                mapName = "horizontalWindShear.mxd"
                varName = "Maximum Airspeed "
                templateMap =os.path.join(mxdDir, "horizontalWindShearTemplate.mxd") 
                mxdcopy = os.path.join(mxdOutput, "HRRR_Maximum_HShear_5000_to_15000")
                dataInput = os.path.join(shapeWindDir,"Maximum_HShear_5000_to_15000.shp")
                layerFile = os.path.join(layerDir, "windshear.lyr")
            elif v == "Maximum_HShear_15000_to_21000":
                mapName = "horizontalWindShear.mxd"
                varName = "Maximum Airspeed "
                templateMap =os.path.join(mxdDir, "horizontalWindShearTemplate.mxd") 
                mxdcopy = os.path.join(mxdOutput, "HRRR_Maximum_HShear_15000_to_21000")
                dataInput = os.path.join(shapeWindDir,"Maximum_HShear_15000_to_21000.shp")
                layerFile = os.path.join(layerDir, "windshear.lyr")
            elif v == "Maximum_Turbulence_5000_to_15000":
                mapName = "turbulenceTemplate.mxd"
                varName = "Maximum Turbulence "
                templateMap =os.path.join(mxdDir, "turbulenceTemplate.mxd") 
                mxdcopy = os.path.join(mxdOutput, "HRRR_Maximum_Turbulence_5000_to_15000")
                dataInput = os.path.join(shapeWindDir,"Maximum_Turbulence_5000_to_15000.shp")
                layerFile = os.path.join(layerDir, "Turbulence.lyr")
            elif v == "Updrafts_Downdrafts" :
                mapName = "updraftTemplate.mxd"
                varName = "Updrafts and Downdrafts "
                templateMap =os.path.join(mxdDir, "updraftTemplate.mxd") 
                mxdcopy = os.path.join(mxdOutput, "HRRR_Updraft_downdraft")
                dataInput = os.path.join(shapeWindDir,"Updrafts_Downdrafts.shp")
                layerFile = os.path.join(layerDir, "Updrafts.lyr")
            elif v == "Horizontal_WindShear" :
                mapName = "horizontalWindShear.mxd"
                varName = "Horizontal Wind Shear "
                templateMap =os.path.join(mxdDir, "horizontalWindShearTemplate.mxd") 
                mxdcopy = os.path.join(mxdOutput, "HRRR_horizontalWindShear")
                dataInput = os.path.join(shapeWindDir,"HorizontalSheer.shp")
                layerFile = os.path.join(layerDir, "windshear.lyr")

            statement = "create map service for " + varName
            logHRRR.main(logFile,statement)
            HRRR_aviation.main(lines,templateMap,dataInput,layerFile,mxdcopy,varName,extension,v,logFile)
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
   






