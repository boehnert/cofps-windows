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
import HRRR_images


# Check out any necessary licenses
arcpy.CheckOutExtension("spatial")
arcpy.env.overwriteOutput = True



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
            #resolution=["40000 40000", "12000 12000","native"]
            resolution=["40000 40000", "12000 12000"]

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
                    newWindName = "S_D_" +str(i) +"_" + lastBit
                    
                    newWind = os.path.join(shapeWindDir,newWindName)
                    print "create file %s" %newWind
                    arcpy.CopyFeatures_management("speed_layer", newWind)
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

