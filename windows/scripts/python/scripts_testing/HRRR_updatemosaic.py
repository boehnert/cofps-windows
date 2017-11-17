
#This script is used to create the maps for the HRRR map services
# called from HRRR_atm
# example  HRRR_images.main(lines,templateMap,dataInput,layerFile,mxdcopy,varName,extension,v,logFile)

#/*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*
# * Copyright (c) 2016 UCAR
# * University Corporation for Atmospheric Research(UCAR)
# * National Center for Atmospheric Research(NCAR)
# * Research Applications Program(RAP)
# * P.O.Box 3000, Boulder, Colorado, 80307-3000, USA
# * All rights reserved. Licenced use only.
# * $Date: 2017-09-20
# *=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*/

# --- Import system modules --- #
import sys
sys.dont_write_bytecode = True
import os
import traceback
import time
import cofps_webService
import cofps_webService2
from shutil import copyfile
import glob
import logHRRR
import HRRR_process
import restartMapService

import agis_utils

import COFPS_config

user = COFPS_config.Ags_usr
passwd = COFPS_config.Ags_pwd
server = COFPS_config.Ags_host
port = 6443


# Import ArcGIS modules and environments
import arcpy
arcpy.env.overwriteOutput = True                                                # Module configurations
# --- End Import system modules --- #

def zoom(addLayer):
    ext = addLayer.getExtent()
    return ext

def main(dataInput,lines,mxdcopy,varName,v,logFile,extension,dataDir,mosaic):
	
    con = "Database Connections\\cofps-web2.rap.ucar.edu.sde\\"
    rasterMosaic = mosaic
    mdname = con + mosaic
    rastype = "Raster Dataset"
    updatecs = "UPDATE_CELL_SIZES"
    updatebnd = "UPDATE_BOUNDARY"
    updateovr = "UPDATE_OVERVIEWS"
    maxlevel = "2"
    maxcs = "#"
    maxdim = "#"
    spatialref = "#"
    inputdatafilter = "*.tif"
    subfolder = "NO_SUBFOLDERS"
    duplicate = "OVERWRITE_DUPLICATES"
    buildpy = "BUILD_PYRAMIDS"
    calcstats = "CALCULATE_STATISTICS"
    buildthumb = "NO_THUMBNAILS"
    comments = "Add Raster Datasets"
    forcesr = "#"
    try:
        #updateMosaic with data
        t = 0
        print "t %s" %t
        listofData = ""
        while t<19:
            #expt ='"DateTime" = ' + "'%s'" %(t)
            timeStep = lines[t+4]
            print "t %s line %s" %(t,timeStep)
            p = HRRR_process.getP(timeStep,t)
            lName = HRRR_process.getName(timeStep,t)

            inpath = dataInput + p + extension
            listofData = listofData +";"+ inpath +";"
            
            t =t +1
        try:
            arcpy.AddRastersToMosaicDataset_management(mdname,  rastype, listofData, "UPDATE_CELL_SIZES", "UPDATE_BOUNDARY", "NO_OVERVIEWS", "", "0", "1500", "", "", "NO_SUBFOLDERS", "OVERWRITE_DUPLICATES", "BUILD_PYRAMIDS", "CALCULATE_STATISTICS", "NO_THUMBNAILS", "", "NO_FORCE_SPATIAL_REFERENCE", "ESTIMATE_STATISTICS", "")
            print "done adding raster %s" %listofData
        except:
            print "problem adding rasters"
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

                        
    except e:
        print "Error when add rasters to mosaic %s" %e
        

##    # Create Map Document and Data Frame objects
##    try:
##        
##        t = 0
##        field = ['objectid','dateTime']
##        print mxdcopy
##        mxd = arcpy.mapping.MapDocument(mxdcopy)
##        df = arcpy.mapping.ListDataFrames(mxd, "Layers")[0]
##        print "got df"
##        for lyr in arcpy.mapping.ListLayers(mxd, "", df):
##            print "layer name %s"%lyr.name
##            if lyr.name == "Footprint":
##                footprintLyr = lyr
##                #update timeDate field in the Footprint
##                print "got it"
##                with arcpy.da.UpdateCursor(lyr,field) as cursor:
##                    for row in cursor:
##                        obj = row[0]
##                        print obj
##                        t = int(obj)-2
##                        timeStep = lines[t+4]
##                        print "t %s line %s" %(t,timeStep)
##                        row[1] = timeStep
##                        cursor.updateRow(row)
##    except:
##        print "problem adding rasters"
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


    try:
        
	service = 'test_HRRR_%s_Current' %v
	print "restart service %s" %service
	#service = "HRRR_test"
        statement = "Restarting service for " + service
        logHRRR.main(logFile,statement)

           
        #return status to tell us if the service published correctly
        #restartMapService.main(service)
        token = agis_utils.get_token(user, passwd, server, port)
        if not token:
            sys.exit(1)
        status = agis_utils.delete_mapservice(service,token,server,port)
        statement = "Returning from publishing map service with Status = %s" %status
        logHRRR.main(logFile,statement)
        print statement
    except :
        print "AN ERROR occured in restartMapService for %s" %v

   
        
# Local variables:
if __name__ == '__main__':
    try:
		#dataInput,lines,mxdcopy,varName,v,logFile
        tic = time.time()
        args = sys.argv
        
        dataInput = args[1]
	log = args[2]
        mxdcopy = args[3]
        varName = args[4]
        v = args[5]
        logFile = args[6]
	extension = args[7]
	dataDir = args[8]
	mosaic = args[9]
        
        main(dataInput,lines,mxdcopy,varName,v,logFile,extension,dataDir,mosaic)
        print 'Time elapsed: %s seconds' %(time.time()-tic)

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
