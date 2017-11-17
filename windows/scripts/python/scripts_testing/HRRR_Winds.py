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
arcpy.env.overwriteOutput = 1

user = COFPS_config.Ags_usr
passwd = COFPS_config.Ags_pwd
server = COFPS_config.Ags_host
port = 6443

try:
    def createPoints(dataDir,inputFile, outputFile, res, fieldName):
        
        if res != "native" :
            print "resample will happen %s" %outputFile
            arcpy.Resample_management(inputFile, outputFile, res, "NEAREST")
        else :
            outputFile = inputFile
        name = os.path.basename(inputFile).split(".")[0]
        shapeName = name + ".shp"
        
        outSpeedShape = os.path.join(dataDir, shapeName)
        arcpy.RasterToPoint_conversion(outputFile, outSpeedShape, "VALUE")
        # Process: Add Field
        arcpy.AddField_management(outSpeedShape, fieldName, "DOUBLE", "", "")
        arcpy.CalculateField_management(outSpeedShape, fieldName, "[GRID_CODE]")

        return outSpeedShape

    def copyFiles(fromDir,toDir):
        #delete any files that are more than 14 days old
        print "copy from %s copy to %s" %(fromDir,toDir)
        for fileName in glob.glob(toDir + os.sep + "S_D_*"):
            os.remove(fileName)
            
        #loop through png's in input directory and copy them over to server
        for ncwpath in glob.glob(fromDir+ os.sep + "S_D_*"):
            fileName = os.path.basename(ncwpath)
            dis = os.path.join(toDir,fileName)
            copyfile(ncwpath, dis)


    def main(shapeWindDir,dataDir,outputMapsDir):
        try:
            skipI = 3
            resolution=["40000 40000", "12000 12000","native"]
            
            db = "Database Connections\\cofps-web2.rap.ucar.edu.sde\\hrrr.sde.Winds_temp"
            dbTo = "Database Connections\\cofps-web2.rap.ucar.edu.sde"

            #loop through winds and convert to points
            for ncwpath in glob.glob(shapeWindDir + os.sep + 'web_WS*.tif'):
                fullName = os.path.basename(ncwpath)
                print fullName
                for i, res in enumerate(resolution):
                    print res
                    print i
                    resampleName = "resample_"+ str(i) + "_" + fullName
                    resampleOut = os.path.join(dataDir,resampleName)

                    print resampleOut
                    outSpeedShape = createPoints(dataDir,ncwpath,resampleOut,res, "speed")
                    arcpy.MakeFeatureLayer_management(outSpeedShape, "speed_layer")
                    #print "back from outDirShape %s" %outSpeedShape
                    
                    lastBit = ncwpath[-6:]
                    dirTiff = "web_WD_10m_Met_" + lastBit
                    
                    dirFullTiff = os.path.join(shapeWindDir, dirTiff)
                    resampleName = "resample_" + str(i) + "_" + dirTiff
                    resampleOut = os.path.join(dataDir, resampleName)

                    outDirShape = createPoints(dataDir,dirFullTiff, resampleOut, res, "direction")
                    #print "back from outDirShape %s" %outDirShape
                    arcpy.MakeFeatureLayer_management(outDirShape, "direction_layer")

                    arcpy.AddJoin_management("speed_layer", "FID", "direction_layer", "FID")
                    dataName = lastBit.split(".")
                    
                    newWindName = "testing_S_D_" +str(i) +"_" + dataName[0] +".shp"
                    newWind = os.path.join(shapeWindDir,newWindName)
                    #print "create file %s" %newWind
                    arcpy.CopyFeatures_management("speed_layer", newWind)
                    
                    #newWindName = "wind_" +str(i) +"_" + dataName[0]
                    #print "new wind name %s" %newWindName

##                    db = "Database Connections\\cofps-web2.rap.ucar.edu.sde\\hrrr.sde.Winds_temp"
##                    #newWindDC = databaseCon + "\\test_1"
##                    newWindDC = fromdatabaseCon + "\\" + newWindName
##                    print "copying %s to %s" %(newWind,newWindDC)
##                   # Process: Copy Features
##                    try:
##                        if arcpy.Exists(newWindDC):
##                            print "deleting file %s" %newWindDC
##                            arcpy.Delete_management(newWindDC)
##                        # Process: Feature Class to Feature Class
##                        print "createing %s" %newWind
##                        arcpy.FeatureClassToFeatureClass_conversion(newWind, db, newWindName)
##
##
##                        #arcpy.CopyFeatures_management(newWind, newWindDC, "", "0", "0", "0")
##                    #arcpy.FeatureClassToFeatureClass_conversion(newWind, databaseCon,newWindName)
##                    except:
##                        print " Copy Feature Failed"
##                         # Get the traceback object
##                        tb = sys.exc_info()[2]
##                        tbinfo = traceback.format_tb(tb)[0]
##
##                        # Concatenate information together concerning the error into a message string
##                        pymsg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n" + str(sys.exc_info()[1])
##                        msgs = "ArcPy ERRORS:\n" + arcpy.GetMessages(2) + "\n"
##
##                        # Return python error messages for use in script tool or Python Window
##                        arcpy.AddError(pymsg)
##                        arcpy.AddError(msgs)
##
##                        # Print Python error messages for use in Python / Python Window
##                        print pymsg + "\n"
##                        print msgs
##                                                         

            #return status to tell us if the service published correctly
            #restartMapService.main(service)
            for i, res in enumerate(resolution):
                service = 'test_HRRR_Wind_Zoom%s_Current' %i
                print "stopping service %s" %service
                token = agis_utils.get_token(user, passwd, server, port)
                if not token:
                    sys.exit(1)
                status = agis_utils.stop_mapservice(service,token,server,port)
                print "stopping service %s" %service
                
                time = 0
                #loop through winds and convert to points
                searchFile = "testing_S_D_%s_*.dbf"%(str(i))
                print "searching for %s"%searchFile
                for ncwpath in glob.glob(shapeWindDir + os.sep + searchFile):
                    fullName = os.path.basename(ncwpath)
                    #print fullName
                    part = fullName.split("_")[4]
                    lastpart = part.split(".")[0]
                    newWindName = "hrrrwind_%s_%s" %(str(i),lastpart)
                    
                    arcpy.env.overwriteOutput = True
                    newFC = os.path.join(dbTo,newWindName)
                    #print newFC
                    # Process: Feature Class to Feature Class
                    ##                    try:
                    if arcpy.Exists(newFC):
                        #print "deleting file %s" %newFC
                        arcpy.Delete_management(newFC)
                    # Process: Feature Class to Feature Class
                    #print "%s %s %s"%(ncwpath,dbTo,newWindName)
                    #arcpy.FeatureClassToFeatureClass_conversion(ncwpath, dbTo, newWindName)
                    arcpy.TableToTable_conversion(ncwpath, dbTo, newWindName)


                    
                    #arcpy.FeatureClassToFeatureClass_conversion(fromWind, dbTo, newWindName)

                print "starting service %s" %service
                status = agis_utils.start_mapservice(service,token,server,port)
            #copyFiles(dataDir,shapeWindDir)
            #HRRR_images.main()


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
        # if len(args) == 2:
        #
        shapeWindDir = args[1]
        dataDir = args[2]
        outputMapsDir = args[3]
       
        main(shapeWindDir,dataDir,outputMapsDir)







except :
    print "ERROR Happenned"
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

