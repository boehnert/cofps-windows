
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
import HRRR_updatemosaic
import HRRR_updateFD



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
#varList = ["Maximum_WW_5000_to_15000_bin","Maximum_WW_15000_to_21000_bin","Maximum_Turbulence_5000_to_15000_bin","Maximum_Turbulence_15000_to_21000_bin","Maximum_HShear_5000_to_15000","Maximum_HShear_15000_to_21000"]
varList = ["TT_2m_F","RH","Wind_Gust","Maximum_WW_5000_to_15000_bin","Maximum_WW_15000_to_21000_bin","Maximum_Turbulence_5000_to_15000_bin","Maximum_Turbulence_15000_to_21000_bin","Maximum_HShear_5000_to_15000_bin","Maximum_HShear_15000_to_21000_bin"]
    
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
        #HRRR_WindsZoom2.main(shapeWindDir,dataDir,mxdOutput)
        print "----Done with Zoom2---"

        
        for v in varList:
            statement = "Working on variable " + v
            print statement
            logHRRR.main(logFile,statement)
            
            
            if v == "Wind_Gust":
                varName = "Wind Gust "
                templateMap =os.path.join(mxdDir, "HRRR_Wind_Gusttemplate.mxd")
                mxdcopy = os.path.join(mxdOutput, "test_HRRR_Wind_Gust.mxd")
                dataInput = os.path.join(shapeWindDir,"web_GUST_MPH_")
                layerFile = os.path.join(layerDir, "T2F.lyr")
                extension = ".tif"
                mosaic = "hrrr.sde.Wind_Gust"
                work = "mosaic"
            elif v == "TT_2m_F":
                varName = "Temperature "
                #templateMap =os.path.join(mxdDir, "HRRR_Temperaturetemplate.mxd")
                mxdcopy = os.path.join(mxdOutput, "test_HRRR_T2F.mxd")
		dataInput = os.path.join(shapeWindDir,"web_TT_2m_F_")
                #layerFile = os.path.join(layerDir, "T2F.lyr")
                extension = ".tif"
                mosaic = "hrrr.sde.TT_2m_F"
                work = "mosaic"
            elif v == "RH":
                varName = "Relative Humidity "
                templateMap =os.path.join(mxdDir, "HRRR_RHtemplate.mxd") 
                mxdcopy = os.path.join(mxdOutput, "test_HRRR_RH.mxd")
                dataInput = os.path.join(shapeWindDir,"web_RH_")
                layerFile = os.path.join(layerDir, "RH.lyr")
                extension = ".tif"
                mosaic = "hrrr.sde.RH"
                work = "mosaic"
           
            elif v == "Maximum_WW_15000_to_21000_bin" :
                varName = "Maximum Updrafts and Downdrafts "
                templateMap =os.path.join(mxdDir, "HRRR_max_updraftTemplate.mxd") 
                mxdcopy = os.path.join(mxdOutput, "test_HRRR_Max_Updraft_downdraft_15000_to_21000")
                dataInput = os.path.join(shapeWindDir,"Maximum_WW_15000_to_21000.shp")
                layerFile = os.path.join(layerDir, "Updrafts.lyr")
                extension = ".shp"
                mosaic = "hrrr.sde.aviation\\hrrr.sde.Maximum_WW_15000_to_21000"
                work = "fd"
            elif v == "Maximum_WW_5000_to_15000_bin" :
                varName = "Maximum Updrafts and Downdrafts "
                templateMap =os.path.join(mxdDir, "HRRR_max_updraftTemplate.mxd") 
                mxdcopy = os.path.join(mxdOutput, "test_HRRR_Max_Updraft_downdraft_5000_to_15000")
                dataInput = os.path.join(shapeWindDir,"Maximum_WW_5000_to_15000.shp")
                layerFile = os.path.join(layerDir, "Updrafts.lyr")
                extension = ".shp"
                mosaic = "hrrr.sde.aviation\\hrrr.sde.Maximum_WW_5000_to_15000"
                work = "fd"
            elif v == "Maximum_Turbulence_15000_to_21000_bin":
                mapName = "turbulenceTemplate.mxd"
                varName = "Maximum Turbulence "
                templateMap =os.path.join(mxdDir, "turbulenceTemplate.mxd") 
                mxdcopy = os.path.join(mxdOutput, "test_HRRR_Maximum_Turbulence_15000_to_21000")
                dataInput = os.path.join(shapeWindDir,"Maximum_Turbulence_15000_to_21000.shp")
                layerFile = os.path.join(layerDir, "Turbulence.lyr")
                extension = ".shp"
                mosaic = "hrrr.sde.aviation\\hrrr.sde.Maximum_Turbulence_15000_to_21000"
                work = "fd"
            elif v == "Maximum_HShear_5000_to_15000_bin":
                mapName = "horizontalWindShear.mxd"
                varName = "Maximum Airspeed "
                templateMap =os.path.join(mxdDir, "horizontalWindShearTemplate.mxd") 
                mxdcopy = os.path.join(mxdOutput, "test_HRRR_Maximum_HShear_5000_to_15000")
                dataInput = os.path.join(shapeWindDir,"Maximum_HShear_5000_to_15000.shp")
                layerFile = os.path.join(layerDir, "windshear.lyr")
                extension = ".shp"
                mosaic = "hrrr.sde.aviation\\hrrr.sde.Maximum_HShear_5000_to_15000"
                work = "fd"
            elif v == "Maximum_HShear_15000_to_21000_bin":
                mapName = "horizontalWindShear.mxd"
                varName = "Maximum Airspeed "
                templateMap =os.path.join(mxdDir, "horizontalWindShearTemplate.mxd") 
                mxdcopy = os.path.join(mxdOutput, "test_HRRR_Maximum_HShear_15000_to_21000")
                dataInput = os.path.join(shapeWindDir,"Maximum_HShear_15000_to_21000.shp")
                layerFile = os.path.join(layerDir, "windshear.lyr")
                extension = ".shp"
                mosaic = "hrrr.sde.aviation\\hrrr.sde.Maximum_HShear_5000_to_15000"
                work = "fd"
            elif v == "Maximum_Turbulence_5000_to_15000_bin":
                mapName = "turbulenceTemplate.mxd"
                varName = "Maximum Turbulence "
                templateMap =os.path.join(mxdDir, "turbulenceTemplate.mxd") 
                mxdcopy = os.path.join(mxdOutput, "test_HRRR_Maximum_Turbulence_5000_to_15000")
                dataInput = os.path.join(shapeWindDir,"Maximum_Turbulence_5000_to_15000.shp")
                layerFile = os.path.join(layerDir, "Turbulence.lyr")
                extension = ".shp"
                mosaic = "hrrr.sde.aviation\\hrrr.sde.Maximum_Turbulence_5000_to_15000"
                work = "fd"

            if work:
                #HRRR_images.main(lines,templateMap,dataInput,layerFile,mxdcopy,varName,extension,v,logFile)
                if work == "mosaic" :
                    HRRR_updatemosaic.main(dataInput,lines,mxdcopy,varName,v,logFile,extension,shapeWindDir,mosaic)
                elif (work == "fd") :
                    print "fd stuff"
                    HRRR_updateFD.main(dataInput,lines,mxdcopy,varName,v,logFile,extension,shapeWindDir,mosaic)
                else :
                    print "wind stuff"
                   

                statement = "Finished making map service for " + varName
                logHRRR.main(logFile,statement)
##
##
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
   
   





