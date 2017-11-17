
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
import HRRR_process


import cofps_Fire_webService


# Import ArcGIS modules and environments
import arcpy
arcpy.env.overwriteOutput = True                                                # Module configurations
# --- End Import system modules --- #

# --- Global Variables --- #

# Data and Map Directories
#dataDir = r"y:\hrrr"                                                 # Directory storing HRRR GIS data
mxdDir = r"E:\cofireop\Mapping\templateMaps"
outputMXD = r"E:\cofireop\Mapping\FireSimulationMaps"
# Directory storing HRRR GIS Map Documents
layerDir = r"E:\cofireop\Mapping\layers"
dataDict = []
mxdList = []

# Individual file locations
mxdname = os.path.join(mxdDir, "Blank_Document.mxd")                            # Base Map Document (10.3 MXD by K. Sampson)
#logfile = os.path.join(dataDir, "HRRR_current_readme.log")                      # HRRR Product Generation Log file

# For Testing
t2fGL = os.path.join(layerDir, "TTGroupLayer.lyr")
t2fLayer = os.path.join(layerDir, "T2F.lyr")

RHGL = os.path.join(layerDir, "RHGroupLayer.lyr")
RHLayer = os.path.join(layerDir, "RH.lyr")

rosGL = os.path.join(layerDir, "ROSGL.lyr")
rosLayer = os.path.join(layerDir, "ROS.lyr")

HRGL = os.path.join(layerDir, "HeatReleaseGL.lyr")
HeatReleaseLayer = os.path.join(layerDir, "HeatRelease_class.lyr")

FlameLengthGL = os.path.join(layerDir, "FlameLenthGL.lyr")
FlameLengthLayer = os.path.join(layerDir, "FlameLength.lyr")

smokeGL = os.path.join(layerDir, "smokeGL.lyr")
smokeLayer = os.path.join(layerDir, "smoke.lyr")

windGL = os.path.join(layerDir, "sim_speedDirGL.lyr")
windLayer = os.path.join(layerDir, "sim_speedDir.lyr")


fireGL = os.path.join(layerDir, "FireBoundaries")

# Service List
serviceList = []
errorList = []


# --- End Global Variables --- #

# --- Main codeblock --- #
def updateMinMax(serviceName):
    print "*****************"
    print "Back from cofps_Fire_webService" 
    #update the service to have a minimum instance of 0
    updateServiceName = serviceName +".MapServer"
    #print "sending %s" %updateServiceName
    
        
    print "Back from publishing services"
    serviceURL = "https://proxy.rap.ucar.edu/arcgis/rest/services/" + serviceName +"/MapServer"
    print "*****************"
    print "Going into UpdateMinMaxInstances"
    updateMinMaxInstances.main(argv=[updateServiceName])
    #add to dictionary[""] =
    print "*****************"
    print "Back from UpdateMinMaxInstances"

    
def getTime(time):
    
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
                
def zoom(addLayer):
    ext = addLayer.getExtent()
    return ext              

def leadTimeInSecondsFromDateTime(time1, time2, dtFormat):
    try:
        
        start = dt.datetime.strptime(time1, dtFormat)
        end = dt.datetime.strptime(time2, dtFormat)
        diff = int((end-start).total_seconds())
        #print "diff is %s" %diff
        return diff
    except ValueError:
        print "invalid date-time value or format"
        return -1

def createDir(fireName,fireID,fireDate,timeNum):
    
    pathCompletePart = os.path.join(fireName,fireID)
    pathCompletePart2 = os.path.join(pathCompletePart,fireDate)
    time = "time"+timeNum
    pathComplete = os.path.join(pathCompletePart2,time)
    makeDirectory = os.path.join(outputMXD,pathComplete)
    if not os.path.exists(makeDirectory):
            os.makedirs(makeDirectory)
    return makeDirectory

def copy_files(indir, outdir):
    #loop through png's in input directory and copy them over to server
        for ncwpath in glob.glob(indir + os.sep + "web*"):
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



def main(allVarList,pickleDir,fireDict,timeNum):
    try:
        start = time.ctime()
        print "***********"
        print "In CreateMaps.py"
        print str(start)
        print "***********"
        product_list = []
        product_list.append(fireDict)
        #get how many arrays are in allVarList
        variableNumbers = len(allVarList)
        tformat = "%Y-%m-%d %H:%M:%S"
        layerOn = False
        
        #loop through variable List
        for varList in allVarList:
            for i,f in enumerate(varList) :
                #print f
                if i == 0 :
                    #get the first line
                    last = False
                    lineArray = f.split(",")
                    dataLoc = lineArray[2]
                    
                    baseName = os.path.basename(dataLoc)
                    dirName = os.path.dirname(dataLoc)
                    #make the new directory string
                    fireDir = dirName.replace("/data","E:")

                    #create the service Array
                    servNameArray = createServiceName(dirName)
                    servName = servNameArray[0]
                    fireName = servNameArray[1]
                    fireID = servNameArray[2]
                    fireDate =servNameArray[3]
                        
                    #create the directory to store the map document for this fire
                    outputDir = createDir(fireName,fireID,fireDate,timeNum)
                    
                    startTime = 0
                    layeron = True
                    lastTime = len(varList) -1
                    

                    #get LeadTime
                    if startTime == lastTime :  #this is the first hour so start == end
                        start = varList[startTime].split(",")[1]
                        end = start
                        leadTime = 0
                        multipleTimes = 0
                        startbits = start.split(" ")
                           # if the timezone is included then remove time zone
                        if len(startbits) == 3 : #remove the time zone
                            start = " ".join(start.split()[:-1])
                            end = start
                    else :
                        start = varList[startTime].split(",")[1]
                        end = varList[lastTime].split(",")[1]
                        #print "LeadTime inputs %s %s" %(start,end)
                        last = True

                        startbits = start.split(" ")
                        endbits = end.split(" ")
                        if len(startbits) == 3 : #remove the time zone
                            start = " ".join(start.split()[:-1])
                            end = " ".join(end.split()[:-1])
                        #print "start = %s  end = %s lead = %s" %(start,end,leadTime)
                        leadTime = leadTimeInSecondsFromDateTime(start, end, tformat)
                        
                    
                    v = baseName.split("_")
                    print v[1]
                    
        
                    if v[1] == "ROS":
                        GLname = rosGL
                        varName = "Rate of Spread "
                        layerFile = rosLayer
                        mapname = os.path.join(mxdDir,"ROStemplate.mxd")
                        mxdcopy = os.path.join(outputDir, "ROS.mxd")
                        fileName = "ROS_FPM"
                        serviceName = "ROS_" + servName
                        summary = "Rate of Spread for fire  %s"  %servName
                        tags = "ROS"
                    elif v[1] == "FGRNHFX":
                        GLname = HRGL
                        varName = "Heat Release "
                        mxdcopy = os.path.join(outputDir, "HeatRelease.mxd")
                        layerFile = HeatReleaseLayer
                        mapname = os.path.join(mxdDir,"HRtemplate.mxd")
                        fileName = "FGRNHFX"
                        serviceName = "HeatRelease_" + servName
                        summary = "Heat Release for fire  %s"  %servName
                        tags = "Heat Release"
                    elif v[1] == "FLAME":
                        GLname = FlameLengthGL
                        varName = "Flame Length "
                        mxdcopy = os.path.join(outputDir, "FlameLength.mxd")
                        layerFile = FlameLengthLayer
                        mapname = os.path.join(mxdDir,"FlameLengthTemplate.mxd")
                        fileName = "FLAME_LENGTH_ft"
                        serviceName = "FlameLength_" + servName
                        summary = "Flame Length for fire  %s"  %servName
                        tags = "Flame Length"
                    elif v[2] == "smoke":
                        GLname = smokeGL
                        varName = "Smoke "
                        mxdcopy = os.path.join(outputDir, "smoke.mxd")
                        layerFile = smokeLayer
                        mapname = os.path.join(mxdDir,"smoke_template.mxd")
                        fileName = "fire_smoke_g_kg"
                        serviceName = "smoke_" + servName
                        summary = "Smoke for fire  %s"  %servName
                        tags = "smoke"
                    elif v[1] == "WS10":
                        GLname = windGL
                        varName = "Wind "
                        mxdcopy = os.path.join(outputDir, "wind.mxd")
                        layerFile = windLayer
                        mapname = os.path.join(mxdDir,"windTemplate.mxd")
                        fileName = "Wind"
                        serviceName = "wind_" + servName
                        summary = "Wind for fire  %s"  %servName
                        tags = "wind"
                        inputFileName = "S_D_"
                    elif v[1] == "T2F":
                        GLname = t2fGL
                        varName = "Temperature "
                        mxdcopy = os.path.join(outputDir, "Temperature.mxd")
                        layerFile = t2fLayer
                        mapname = os.path.join(mxdDir,"t2fTemplate.mxd")
                        fileName = "T2F"
                        serviceName = "T2F_" + servName
                        summary = "Temperature for fire  %s"  %servName
                        tags = "Temperature"
                    elif v[1] == "RHsfc":
                        GLname = RHGL
                        varName = "Relative Humidity "
                        mxdcopy = os.path.join(outputDir, "RHsfc.mxd")
                        layerFile = RHLayer
                        mapname = os.path.join(mxdDir,"RHsfcTemplate.mxd")
                        fileName = "RHsfc"
                        serviceName = "RHsfc_" + servName
                        summary = "Relative Humidity for fire  %s"  %servName
                        tags = "Relative Humidity"
                                   

                    # Create Map Document and Data Frame objects
                    #print "map Name %s" %mapname
                    mxd = arcpy.mapping.MapDocument(mapname)
                    df = arcpy.mapping.ListDataFrames(mxd, "Layers")[0]
                    fireGroupLayer = arcpy.mapping.ListLayers(mxd, "", df)[0]
                    
                #split up the input line based on ,
                lineArray = f.split(",")
                #the data location variable
                dataLoc = lineArray[2]  
                baseName = os.path.basename(dataLoc)
                
                #set up time for layer name
                timeSplit = f.split(",")
                getTimeI = timeSplit[0].split(" ")[1]
                pTime = getTimeI[-2:]  #index
                
                p = pTime
                #lName = HRRR_process.getName(timeSplit[1],p)
                timeStep = "Time " + str(p) + " " + timeSplit[1]
                
                if v[1] == "WS10" :
                    bit = baseName.split("_")[3]
                    lastBit = bit.split(".")[0]
                    baseName = "S_D_" + lastBit + ".shp"
                    fireVar = os.path.join(fireDir, baseName)
                else :
                    fireVar = os.path.join(fireDir, baseName)
                
                addLayer = arcpy.mapping.Layer(fireVar)
                if addLayer.isRasterLayer:
                    #set up symbology for raster layer 
                    arcpy.CalculateStatistics_management(addLayer.dataSource)
                    elevSTDResult = arcpy.GetRasterProperties_management(fireVar, "MAXIMUM")
                    #Get the elevation standard deviation value from geoprocessing result object
                    elevMax = elevSTDResult.getOutput(0)
                    updateLayer = addLayer
                    sourceLayer = arcpy.mapping.Layer(layerFile)
                    arcpy.mapping.UpdateLayer(df, updateLayer, sourceLayer, True)
                else:
                    #set up symbology for vector layer
                    arcpy.ApplySymbologyFromLayer_management(addLayer, layerFile)
                
               
                newName = timeStep
                
                addLayer.name = newName
                if i == 1 :
                    addLayer.visible = True
                else :
                    addLayer.visible = False
                arcpy.mapping.AddLayerToGroup(df, fireGroupLayer, addLayer, "BOTTOM")

            ext = zoom(addLayer)
            df.extent = ext            
            arcpy.RefreshTOC()
            arcpy.RefreshActiveView()


            # Save Group Layer and Map
            mxd.saveACopy(mxdcopy)
            print 'Saving to %s' %mxdcopy
            print "*****************"
            print "Now go to publish %s" %serviceName
            
            try :
                #return status to tell us if the service published correctly
                status = cofps_Fire_webService.main(mxdcopy,serviceName,summary,tags)
            except :
                print "AN ERROR occured in cofps_Fire_webService.main for %s" %serviceName

            try:
                if status == False :  #there was a problem during publishing
                    print "adding service to error log %s" %serviceName
                    errorList.append([mxdcopy,serviceName,summary,tags])
                else :  #there was no problem
                    print "service %s published okay" %serviceName
                    #updateMinMax(serviceName)
                    serviceURL = "https://proxy.rap.ucar.edu/arcgis/rest/services/" + serviceName +"/MapServer"
                
                    dataDict = {
                        "name" : varName,
                        "startDateTime" : start,
                        "leadTimeInSeconds": leadTime,
                        "format": 'ags',
                        "url":serviceURL,
                        "type" : 'simulation'
                    }

                    product_list.append(dataDict)
            except :
                print "AN ERROR occured in updateMINMAX or the dataDic portion for %s" %serviceName


                

        #loop through the error list and try to publish again this is the final time we will try to publish the map services
        ap = False
        
        for error in errorList :
            mxdDoc = error[0]
            try:
                for mxd in mxdList :
                    if mxd == mxdDoc :
                        ap = True
                    else :
                        ap = False
                if ap == False :
                    mxdList.append(mxdDoc)
                    print"************************************"
                    print "Rerunning the publishing for %s" %error[0]
                    print"************************************"
                    status = cofps_Fire_webService.main(error[0],error[1],error[2],error[3])
                    print"************************************"
                    print "If status is True than it published OKAY.  STATUS = %s" %status
                    print"************************************"
                    # if status is NONE than there are no error and we can updateMINMAX
                    if status == True :
                        updateMinMax(serviceName)
                        serviceURL = "https://proxy.rap.ucar.edu/arcgis/rest/services/" + serviceName +"/MapServer"
               
                        dataDict = {
                            "name" : varName,
                            "startDateTime" : start,
                            "leadTimeInSeconds": leadTime,
                            "format": 'ags',
                            "url":serviceURL,
                            "type" : 'simulation'
                        }

                        product_list.append(dataDict)
            except :
                print "AN ERROR occured in updateMINMAX or the dataDic portion for %s" %serviceName


            #write out serviceLit to text file
        
        outputPickle = os.path.join(pickleDir,"publish_list.pkl")
        try:
            usePickle(product_list,outputPickle)
        except:
            print "ERROR in usePickle"
        
        

    except Exception as e:
        print e
        print "ERROR IN HERE"
        ##         # Get the traceback object
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
        ##
        ##        # Concatenate information together concerning the error into a message string
        

# Local variables:
if __name__ == '__main__':
    #try:
    args = sys.argv
    #FGRNHFXList,ROSList
    allVarList = args[1]
    outDir = args[2]
    fireDict = args[3]
    timeNum = args[4]

    #tic = time.time()
    main(allVarList,outDir,fireDict,timeNum)
    
