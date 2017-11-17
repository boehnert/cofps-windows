
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
from shutil import copyfile
import glob
import cPickle
import pickle
import datetime as dt
import updateMinMaxInstances


import cofps_Fire_webService


# Import ArcGIS modules and environments
import arcpy
arcpy.env.overwriteOutput = True                                                # Module configurations
# --- End Import system modules --- #

# --- Global Variables --- #

# Data and Map Directories
#dataDir = r"y:\hrrr"                                                 # Directory storing HRRR GIS data
mxdDir = r"E:\cofireop\Mapping\templateMaps"
mxdOutput =r"E:\cofireop\Mapping\FireSimulationMaps"
# Directory storing HRRR GIS Map Documents
layerDir = r"E:\cofireop\Mapping\layers"
dataDict = []

# Individual file locations
mapname = os.path.join(mxdDir, "FireArea_template.mxd")                            # Base Map Document (10.3 MXD by K. Sampson)
#logfile = os.path.join(dataDir, "HRRR_current_readme.log")                      # HRRR Product Generation Log file

fireGL = os.path.join(layerDir, "FireBoundaries")

# Service List
serviceList = []


# --- End Global Variables --- #

# --- Main codeblock --- #
def getTime(time):
    #stTime = strow.split(",")[0]
    #startTimeStep = stTime.split(":")[0]
           
    #if (startTimeStep == 'Timestep 000') :
    #    startTime =stTime.split(":")[1]

    eTime = time.split(",")[0]
    #print "eTime %s" %eTime
            
    endTimeStep = eTime.split(":")[0]
    #print "endTimeStep %s"%endTimeStep
    endbit = endTimeStep.split(" ")[1]
    #print "endbit %s" %endbit
    if (endbit <> 'Independent') :
        endTime =eTime.split(":")[1]
        #print "endTime %s" %endTime
    return endTime
                
               

def leadTimeInSecondsFromDateTime(time1, time2, dtFormat):
    try:
        
        #t1 = "2016-09-01 17:00:00"
        #t2 = "2016-09-01 18:00:00"
          
        start = dt.datetime.strptime(time1, dtFormat)
        end = dt.datetime.strptime(time2, dtFormat)
        
        diff = int((end-start).total_seconds())
        #print "diff is %s" %diff
        
        return diff
    except ValueError:
        print "invalid date-time value or format"
        return -1

def createDir(fireName,fireID,fireDate):
    
    pathCompletePart = os.path.join(fireName,fireID)
    pathComplete = os.path.join(pathCompletePart,fireDate)
    makeDirectory = os.path.join(mxdOutput,pathComplete)
    if not os.path.exists(makeDirectory):
            os.makedirs(makeDirectory)
    return makeDirectory

def copy_files(indir, outdir):
    #loop through png's in input directory and copy them over to server
        for ncwpath in glob.glob(indir + os.sep + "Fire_Area*"):
            fileName = os.path.basename(ncwpath)
            dis = os.path.join(outdir,fileName)
            #print dis
            #print ncwpath
            copyfile(ncwpath, dis)

def createServiceName(dirName) :
    fireArray = dirName.split("/")
    fireName = fireArray[5]
    fireID = fireArray[6]
    fireDate = fireArray[7]
    serviceName = fireID +"_"+ fireDate
    print "Service Name %s" %serviceName
    returnArray = []
    returnArray.append(serviceName)
    returnArray.append(fireName)
    returnArray.append(fireID)
    returnArray.append(fireDate)
    return returnArray

def usePickle(dataDict,outputPickle):
    f = open(outputPickle, "wb")
    pickle.dump(dataDict, f)
     #with open(outputPickle, "wb") as fp:
     #   cPickle.dump(dataDict, fp, protocol=cPickle.HIGHEST_PROTOCOL)



def main(fireData,pickleDir):
    try:
        start = time.ctime()
        print "***********"
        print str(start)
        print "In CreateMaps_fireBoundary.py"
        print "***********"
        #/data/cofireop/sim/gisdata/Test_fire/57cd91c2c9e77c0037a058ff/2016090515/Fire_Area.shp
        tformat = "%Y-%m-%d %H:%M:%S"
        
        varName = "Fire Boundary "
        
        mxd = arcpy.mapping.MapDocument(mapname)
        df = arcpy.mapping.ListDataFrames(mxd, "Layers")[0]
        fireGroupLayer = arcpy.mapping.ListLayers(mxd, "", df)[0]
                                                     
        fireAreasymbologyLayer = os.path.join(layerDir, "FireBoundaries")
        name_field = 'Timestep'
        fields = ['DateTime','Timestep']
        emptyGL = os.path.join(layerDir, "EmptyGL.lyr")

        baseName = os.path.basename(fireData)
        dirName = os.path.dirname(fireData)
        #make the new directory string
        fireDir = dirName.replace("/data","E:")

        #create the service Array set up variables for Service
        servNameArray = createServiceName(dirName)
        servName = servNameArray[0]
        fireName = servNameArray[1]
        fireID = servNameArray[2]
        fireDate =servNameArray[3]
        varName = "Fire Boundary "
        serviceName = "Fire_Boundary_" + servName
        summary = "FireBoundar for fire %s"  %servName
        tags = "Fire Boundary"
                        
        #create the directory to store the map document for this fire
        outputDir = createDir(fireName,fireID,fireDate)
        mxdcopy = os.path.join(outputDir, "FireBoundary.mxd")

        #copy Fire Area to new directory
        copy_files(fireDir, outputDir)

        #set up variable for cursor           
        start = "2010-09-01 17:15:00"
        end = "2010-09-01 17:15:00"
        fireArea = os.path.join(outputDir,"Fire_Area.shp")
        name_field = 'Timestep'
        fields = ['DateTime', 'Timestep']
        # do it to Fire Area
        p = 0
        with arcpy.da.SearchCursor(fireArea, fields) as cursor:
            
            for i,row in enumerate(cursor):
                
                # Print the name of the residential road
                layerFile = fireAreasymbologyLayer + "_" + str(p) + ".lyr"
                addLayer = arcpy.mapping.Layer(fireArea)
                arcpy.ApplySymbologyFromLayer_management(addLayer, layerFile)
                if i == 0 :
                    start = row[0]
                    multipleTimes = 0
                    startbits = start.split(" ")
                   
                    if len(startbits) == 3 : #remove the time zone
                        start = " ".join(start.split()[:-1])
                
                end = row[0]
                end = row[0]
                endbits = end.split(" ")
                if len(endbits) == 3 : #remove the time zone
                    end = " ".join(end.split()[:-1])
                timeStep = row[0]
                
                
                #check if layer has already been mapped
                if multipleTimes == timeStep :
                    print "already mapped this timestep"
                else :
                    multipleTimes = row[0]
                    i = row[1]
                    newI = i 
                    if i < 10 :
                        pTime = "Time 0" + str(newI)
                    else :
                        pTime = "Time " + str(newI)
                    
                    #newName = varName + str(pTime) + " " + timeStep
                    newName = str(pTime) + " " + timeStep
                    print "Layer name %s" %newName
                    time.sleep(3)
                    addLayer.name = newName
                    addLayer.definitionQuery = '"Timestep" = ' + str(i)

                    addLayer.visible = True
                    #if os.path.exists(layerFile):
                    arcpy.mapping.AddLayerToGroup(df, fireGroupLayer, addLayer, "BOTTOM")
                    
                    #print str(p)
                    p = p + 1
                    if (p == 8):
                        p = 0
        print "start %s end %s" %(start,end)  
        leadTime = leadTimeInSecondsFromDateTime(start, end, tformat)
        print "leadTime %s"%leadTime
        time.sleep(3)
        
        arcpy.RefreshTOC()
        arcpy.RefreshActiveView()


        # Save Group Layer and Map
        mxd.saveACopy(mxdcopy)
        print 'Saving to %s' %mxdcopy
              
        print "Now go to publish %s" %serviceName

        cofps_Fire_webService.main(mxdcopy,serviceName,summary,tags)
        #update the service to have a minimum instance of 0
        updateServiceName = serviceName +".MapServer"
        print "sending %s" %updateServiceName
        updateMinMaxInstances.main(argv=[updateServiceName])
                
        print "Back from publishing services"
        serviceURL = "https://proxy.rap.ucar.edu/arcgis/rest/services/" + serviceName +"/MapServer"
        serviceList.append(serviceURL)
        #add to dictionary[""] =
        print "%s %s %s %s " %(varName,start,leadTime,serviceURL)
        time.sleep(3)
        dataDict = {
            "name" : varName,
            "startDateTime" : start,
            "leadTimeInSeconds": leadTime,
            "format": 'ags',
            "url":serviceURL,
            "type" : 'simulation'
        }

        
        return dataDict


    except Exception as e:
        print e
        print " IN HERE"
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

# Local variables:
if __name__ == '__main__':
    try:
        args = sys.argv
        #FGRNHFXList,ROSList
        allVarList = args[1]
        outDir = args[2]
        start = args[3]

        tic = time.time()
        main(allVarList,outDir)
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
