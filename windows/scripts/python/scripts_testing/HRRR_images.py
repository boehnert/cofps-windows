
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

# Import ArcGIS modules and environments
import arcpy
arcpy.env.overwriteOutput = True                                                # Module configurations
# --- End Import system modules --- #

def zoom(addLayer):
    ext = addLayer.getExtent()
    return ext

def main(lines,mxdname,dataInput,layerFile,mxdcopy,varName,extension,v,logFile):
    try:
        
        # Create Map Document and Data Frame objects
        mxd = arcpy.mapping.MapDocument(mxdname)
        df = arcpy.mapping.ListDataFrames(mxd, "Layers")[0]

        GL = arcpy.mapping.ListLayers(mxd, "", df)[0]
        t = 0
        print "t %s" %t
        while t<19:
            #expt ='"DateTime" = ' + "'%s'" %(t)
            timeStep = lines[t+4]
            print "t %s line %s" %(t,timeStep)
            p = HRRR_process.getP(timeStep,t)
            lName = HRRR_process.getName(timeStep,t)
            
            dataInput_new = dataInput + p + extension
            print dataInput_new
            addLayer = arcpy.mapping.Layer(dataInput_new)
                    
            # Read the forecast time of each timestep
            addLayer.name = lName
            arcpy.ApplySymbologyFromLayer_management(addLayer, layerFile)
            arcpy.mapping.AddLayerToGroup(df, GL, addLayer, "BOTTOM")
            ext = zoom(addLayer)
            df.extent = ext 
            
            arcpy.RefreshTOC()
            arcpy.RefreshActiveView()
            t =t+1
    
        print 'Saving to %s ' %(mxdcopy)
        mxd.saveACopy(mxdcopy)
    except:
        statement = "Error when maping map %s" %mxdname
        logHRRR.main(logFile,statement)
            


    try:
        print "going into publishing"
        statement = "Starting to publish map service for " + v
        logHRRR.main(logFile,statement)

           
        #return status to tell us if the service published correctly
        status = cofps_webService.main(mxdcopy,v,logFile)
        statement = "Returning from publishing map service with Status = %s" %status
        logHRRR.main(logFile,statement)
    except :
        print "AN ERROR occured in cofps_Fire_webService.main for %s" %v

    try:
        if status == False :  #there was a problem during publishing
            statement = "trying to publish one more time %s" %v
            logHRRR.main(logFile,statement)
                
            #return status to tell us if the service published correctly
            status = cofps_webService.main(mxdcopy,v,logFile)
            statement = "Second time publishing results in %s (if Trus then it is okay)" %status
            logHRRR.main(logFile,statement)
        else :  #there was no problem
            statement = "service %s published okay" %v
            logHRRR.main(logFile,statement)
                            
    except:
        statement = "Error when publishing a second time %s.  Try again in 1 hour" %serviceName
        logHRRR.main(logFile,statement)
   
        
# Local variables:
if __name__ == '__main__':
    try:

        tic = time.time()
        args = sys.argv
        log = args[1]
        tempMap = args[2]
        dataInput = args[3]
        layerFile = args[4]
        mxdcopy = args[5]
        varName = args[6]
        extension = args[7]
        v = args[8]
        logFile = args[9]
        
        main(log,tempMap,dataInput,layerFile,mxdcopy,varName,extension,v,logFile)
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
