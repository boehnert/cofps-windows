
# ---------------------------------------------------------------------------
#
# ---------------------------------------------------------------------------

# --- Import system modules --- #
import sys
sys.dont_write_bytecode = True
import os
import traceback
import time
import cofps_webService
import createSimWinds
from shutil import copyfile
import glob
import deleteMapService

#import generateImages_FireBoundary
import createMaps
import createMaps_fireBoundary
# Import ArcGIS modules and environments
import arcpy
arcpy.env.overwriteOutput = True                                                # Module configurations
# --- End Import system modules --- #

# --- Global Variables --- #

# Variables to process
FireList = []
ROSList = []
FGRNHFXList = []
flameList = []
smokeList = []
allVarList = []
fireDict = []
windList = []
t2fList = []
RHList = []

#


# --- End Global Variables --- #

# --- Main codeblock --- #
def read_txt(logfile):
    '''Function to read the contents of the HRRR Readme file, which contains the
    times of each forecast hour.'''
    fo = open(logfile, "r")
    lines = fo.readlines()
    fo.close()
    return lines



def main(inputFile):
    start = time.ctime()
    print "***********"
    print str(start)
    print "in readFile.py"
    print "***********"
    
    writeOutDir = os.path.dirname(inputFile)
    #read the lines from product_list.txt
    lines =  read_txt(inputFile)
    #loop through the lines
    for f in lines :
        #print f
        #split the line between time [1] and file location [2]
        lineArray = f.split(",")
        if len(lineArray) == 2 :  #if the file is the time independent files like fire perimeter
            #get name of the file
            basename = os.path.basename(lineArray[1])
            #get the simid
            
        else :
            basename = os.path.basename(lineArray[2])

        base = basename.split("_")
        #print basename
        if basename.strip() == "Fire_Area.shp":
            fireDict = createMaps_fireBoundary.main(lineArray[1],writeOutDir)
            #FireList.append(f)
        if base[0] == "web" :
            timeStep = lineArray[0].split(" ")
            timeNum = timeStep[1]
            
            if base[1] == "ROS":
                if base[2] == "FPM" :
                    #print "do something to %s" %basename
                    ROSList.append(f)
            elif base[1] == "FGRNHFX":
                #print "do something to %s" %basename
                FGRNHFXList.append(f)
            elif base[1] == "FLAME":
                #print "do something to %s" %basename
                flameList.append(f)
            elif base[2] == "smoke":
                #print "do something to %s" %basename
                smokeList.append(f)
            elif base[1] == "WS10" :
                windList.append(f)
            elif base[1] == "T2F" :
                t2fList.append(f)
            elif base[1] == "RHsfc" :
                RHList.append(f)

    createSimWinds.main(windList)
    if len(FGRNHFXList) > 0 :
        allVarList.append(FGRNHFXList)
    if len(ROSList) > 0 :
        allVarList.append(ROSList)
    if len(flameList) > 0 :
        allVarList.append(flameList)
    if len(smokeList) > 0 :
        allVarList.append(smokeList)
    if len(windList) > 0 :
        allVarList.append(windList)
    if len(t2fList) > 0 :
        allVarList.append(t2fList)
    if len(RHList) > 0 :
        allVarList.append(RHList)
    print "going into createMap"
    createMaps.main(allVarList,writeOutDir,fireDict,timeNum)
    



# Local variables:
if __name__ == '__main__':
    try:
        args = sys.argv
        inFile = args[1]

        tic = time.time()
        main(inFile)
        print 'Time elapsed: %s seconds' %(time.time()-tic)

    except Exception as e:
        print e

        print "ERROR Happenned"
    ##         # Get the traceback object
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
    ##
    ##        # Concatenate information together concerning the error into a message string
        pymsg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n" + str(sys.exc_info()[1])
        msgs = "ArcPy ERRORS:\n" + arcpy.GetMessages(2) + "\n"
    ##
    ##        # Return python error messages for use in script tool or Python Window
        arcpy.AddError(pymsg)
        arcpy.AddError(msgs)
    ##
    ##        # Print Python error messages for use in Python / Python Window
        print pymsg + "\n"
        print msgs
