#This script is used to create the wind shapefiles for HRRR 
# called from HRRR_atm
# example HRRR_Winds.main(shapeWindDir,dataDir,mxdOutput)

#/*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*
# * Copyright (c) 2016 UCAR
# * University Corporation for Atmospheric Research(UCAR)
# * National Center for Atmospheric Research(NCAR)
# * Research Applications Program(RAP)
# * P.O.Box 3000, Boulder, Colorado, 80307-3000, USA
# * All rights reserved. Licenced use only.
# * $Date: 2017-09-20
# *=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*/

import arcpy, os, gc, sys, traceback, glob, subprocess, os

from arcpy import env
from arcpy.sa import *

import glob
import logHRRR
import HRRR_process
import restartMapService

import agis_utils

import COFPS_config


# Check out any necessary licenses
arcpy.CheckOutExtension("spatial")
arcpy.env.overwriteOutput = True

holdData = r"E:\cofireop\Mapping\data\standByDatatesting.shp"

user = COFPS_config.Ags_usr
passwd = COFPS_config.Ags_pwd
server = COFPS_config.Ags_host
port = 6443

def getCount(dataInput,expression) :
    #add def Query
    print "print %s" %expression
   
    count = 0
    with arcpy.da.SearchCursor(dataInput, "Timestep", expression) as cursor:  
        for row in cursor:  
            count = count + 1  
    print "get Count count %s" %count
    return count

def main(dataInput,lines,mxdcopy,varName,v,logFile,extension,dataDir,mosaic):
    try:
        #get the connection to the Feature Dataset
        con = "Database Connections\\cofps-web2.rap.ucar.edu.sde\\"
        toDB = con + mosaic
                

        service = 'test_HRRR_%s_Current' %v
        token = agis_utils.get_token(user, passwd, server, port)
        if not token:
            sys.exit(1)
        status = agis_utils.stop_mapservice(service,token,server,port)
        print "stopping service %s" %service
        #delete features in FC
        print "deleting features from %s" %toDB
        arcpy.DeleteFeatures_management(toDB)
        #statement = "Returning from stoping map service with Status = %s" %status
        #logHRRR.main(logFile,statement)
        t=0
        while t<19:
            expression = '"Timestep" = %s' %(t)
            count = getCount(dataInput,expression)
            print "%s have %s features"%(expression,count)
            #if there is no feature for this time add the hold data
            if count == 0:
                print "copy features from hold"
                arcpy.management.MakeFeatureLayer(holdData, "new_layer",expression)
                #arcpy.management.CopyFeatures("new_layer", toDB)
                arcpy.Append_management("new_layer", toDB) 

            else:
                print "copy features from %s" %dataInput
                arcpy.management.MakeFeatureLayer(dataInput, "new_layer",expression)
                arcpy.Append_management("new_layer", toDB)
                #arcpy.management.CopyFeatures("new_layer", toDB)
            t=t+1
                
        
        
        
            
        status = agis_utils.start_mapservice(service,token,server,port)

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
