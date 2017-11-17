
# ---------------------------------------------------------------------------
#
# ---------------------------------------------------------------------------


import arcpy, os, gc, sys, traceback, glob, subprocess, os

from arcpy import env
from arcpy.sa import *
import generateImages_HRRR_2


# Check out any necessary licenses
arcpy.CheckOutExtension("spatial")
arcpy.env.overwriteOutput = True


shapeWindDir = r"E:\cofireop\hrrr\gisdata"
dataDir = r"E:\cofireop\Mapping\data"
outputMapsDir = r"E:\cofireop\Mapping\HRRRMaps"


try:
    def createPoints(inputFile, outDir, fieldName):
        
        name = os.path.basename(inputFile).split(".")[0]
        shapeName = name + ".shp"
        inFile = os.path.join(outDir,inputFile)
        outSpeedShape = os.path.join(outDir, shapeName)
        arcpy.RasterToPoint_conversion(inFile, outSpeedShape, "VALUE")
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


    def main(windList):
        try:
            #windShapeList = []
            #loop through winds and convert to points
            for f in windList:
                fullName = os.path.basename(ncwpath)
                for i, res in enumerate(resolution):

                    lineArray = f.split(",")
                    dataLoc = lineArray[2]
                    
                    baseName = os.path.basename(dataLoc)
                    dirName = os.path.dirname(dataLoc)
                    lastBit = baseName.split("_")[3]
                    newWindName = "S_D_" +str(i) +"_" + lastBit
                    windPoints = os.path.join(dirName,newWindName)
                    if os.path.isfile(windPoints):
                        print "it exists"
                    else:
                        outSpeedShape = createPoints(baseName, dirName, "speed")
                        arcpy.MakeFeatureLayer_management(outSpeedShape, "speed_layer")

                        lastBit = baseName.split("_")[3]
                        dirTiff = "web_WD10_Met_" + lastBit
                        
                        dirFullTiff = os.path.join(dirName, dirTiff)
                        outDirShape = createPoints(dirTiff, dirName, "direction")
                        arcpy.MakeFeatureLayer_management(outDirShape, "direction_layer")

                        arcpy.AddJoin_management("speed_layer", "FID", "direction_layer", "FID")
                        
                    
                    
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
        windList = args[1]
        #
        # elif len(args) > 2:
        #     print "Must specify enough parameters"
        #
        #
        # print "Length of args %s " %len(args)
        # if len(args) == 2:
            main(windList)







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

