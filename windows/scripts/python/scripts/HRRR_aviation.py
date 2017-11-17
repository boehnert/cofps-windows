
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
import logHRRR
import HRRR_process
import cofps_webService2


import cofps_webService


# Import ArcGIS modules and environments
import arcpy
arcpy.env.overwriteOutput = True                                                # Module configurations
# --- End Import system modules --- #

# --- Global Variables --- #

# Data and Map Directories
#dataDir = r"y:\hrrr"
holdData = r"E:\cofireop\Mapping\data\standByData.shp"
  
# Directory storing HRRR GIS data
mxdDir = r"E:\cofireop\Mapping\templateMaps"
mxdOutput =r"E:\cofireop\Mapping\HRRRMaps"
# Directory storing HRRR GIS Map Documents
layerDir = r"E:\cofireop\Mapping\layers"
inputDir = r"E:\cofireop\hrrr\gisdata"
#inputDir = r"C:\cofps\data\Aviation"
logfile = os.path.join(inputDir, "HRRR_current_readme.log")      


varList = ["Maximum_WW_5000_to_15000","Maximum_WW_15000_to_21000","Maximum_HShear_5000_to_15000","Maximum_HShear_15000_to_21000","Maximum_Turbulence_15000_to_21000","Maximum_Turbulence_5000_to_15000","Horizontal_WindShear","Updrafts_Downdrafts","Turbulence"]
#varList = ["Maximum_WW_5000_to_15000"]
flightList = ["5000","7000","9000","11000","13000","15000","17000","19000","21000"]
#flightList = ["9000"]


# --- End Global Variables --- #
def read_txt(logfile):
    '''Function to read the contents of the HRRR Readme file, which contains the
    times of each forecast hour.'''
    fo = open(logfile, "r")
    lines = fo.readlines()
    fo.close()
    return lines

def unique_values(table, fieldnames,level):
    expression = '"FLevel" = ' + level
    with arcpy.da.SearchCursor(table, fieldnames, where_clause=expression) as cursor:
        return sorted({row[0] for row in cursor})

def unique_values_flight(table, fieldnames):
    with arcpy.da.SearchCursor(table, fieldnames) as cursor:
        return sorted({row[0] for row in cursor})

def removeAllLayers(mxd):
    for df in arcpy.mapping.ListDataFrames(mxd):
        for lyr in arcpy.mapping.ListLayers(mxd, "", df):
            if lyr.isGroupLayer :
                for sublyr in lyr :
                    arcpy.mapping.RemoveLayer(df, sublyr)
    mxd.save()
    return mxd

def read_txt(logfile):
    '''Function to read the contents of the HRRR Readme file, which contains the
    times of each forecast hour.'''
    fo = open(logfile, "r")
    lines = fo.readlines()
    fo.close()
    return lines

def addPlaceHolder(timeStep,t) :
    print holdData
    addLayer = arcpy.mapping.Layer(holdData)
    lName = HRRR_process.getName(timeStep,t)
    print lName
    #lName = "N/A"
    addLayer.name = "%s" %lName
    layerFile = os.path.join(layerDir, "standByData.lyr")       
    #apply symbology
    arcpy.ApplySymbologyFromLayer_management(addLayer, layerFile)
    addLayer.visible = True
    return addLayer

def getCount(dataInput,addLayer2,expression) :
    #add def Query
    print "print %s" %expression
   
    #get all the valid times for this flight level
    #result = arcpy.GetCount_management(addLayer2)

    #count = int(result.getOutput(0))
    count = 0
    with arcpy.da.SearchCursor(dataInput, "Timestep", expression) as cursor:  
        for row in cursor:  
            count = count + 1  
    print "get Count count %s" %count
    return count

def zoom(newExtent):
    
    newExtent.XMin, newExtent.YMin = -12306572.308670, 4319493.770429
    newExtent.XMax, newExtent.YMax = -11245300.086768, 5126378.643261
    return newExtent

def getTime(dataInput,expression, fieldname) :
    print expression
    with arcpy.da.SearchCursor(dataInput, fieldname,where_clause=expression) as cursor:
        for row in cursor:
            uniqueValues = row[0]
    return uniqueValues
def main(lines,mxdname,dataInput,layerFile,mxdcopy,varName,extension,v,logFile):
    try:
        # Create Map Document and Data Frame objects
        mxd = arcpy.mapping.MapDocument(mxdname)
        layerBlankFile = os.path.join(layerDir, "empty.lyr")
        print "working on map doc %s" %mxdname           
         #check if the layer is a bin layer
        bins = v.split("_")
        #if working with one of the maximum aviation products
        if (bins[0] == "Maximum") :
            #set up mapping variables
            print "variable = %s" %v
            mxd = removeAllLayers(mxd)
            df = arcpy.mapping.ListDataFrames(mxd, "Layers")[0]
            GL = arcpy.mapping.ListLayers(mxd, "", df)[0]    
            addLayer = arcpy.mapping.Layer(dataInput)
            expression = ""
            #check that there are any data in the file
            count = getCount(dataInput,addLayer,expression)
            #set up a default altitute
            f = "5000"
            #used in looping i is for visibility
            i = 0
            # t is used for time
            t=0
            #loop through the 19 time slices  
            while t<19:
                #get the time from the input lines array
                timeStep = lines[t+4]
                expression = '"Timestep" = %s' %(t)
                #checking if there is data in the file
                count = getCount(dataInput,addLayer,expression)
                #print "count at flight level %s %s" %(t,count)
                #if there are features then do something
                if count > 0 :
                    addLayer = arcpy.mapping.Layer(dataInput)
                    addLayer.definitionQuery = None
                    arcpy.ApplySymbologyFromLayer_management(addLayer, layerFile)
                    print "t %s line %s" %(t,timeStep)
                    p = HRRR_process.getP(timeStep,t)
                    lName = HRRR_process.getName(timeStep,t)
                    #addLayer.name = newName
                    addLayer.name = lName
                    addLayer.definitionQuery = expression
                    #set up visibility                
                    if (i == 0) :
                        addLayer.visible = True
                    else :
                        addLayer.visible = False
                    arcpy.mapping.AddLayerToGroup(df, GL, addLayer, "BOTTOM")
                    
                    i = i + 1
                else :
                    #if no data then set up the placeholder shapefile and mapping
                    addBlankLayer = addPlaceHolder(timeStep,t)
                    arcpy.ApplySymbologyFromLayer_management(addBlankLayer, layerBlankFile)
                    arcpy.mapping.AddLayerToGroup(df, GL, addBlankLayer, "BOTTOM")
                    #print "adding layer %s" %addBlankLayer.name
                    
                t=t+1
                
            

            f= "bin"
            mxdMap = mxdcopy + "_" + f + ".mxd"
            #print mxdMap
            v2 = v +"_"+f
	    newExtent = df.extent
            ext = zoom(newExtent)
            df.extent = ext 
            arcpy.RefreshTOC()
            arcpy.RefreshActiveView()

            # Save Group Layer and Map
            mxd.saveACopy(mxdMap)
            print "*******"
            print 'Saving to %s' %mxdMap
            try:
                statement = "Creating Web Service for %s " %v2
                print statement
                logHRRR.main(logFile,statement)
                cofps_webService.main(mxdMap,v2,logFile)
                #cofps_webService2.main(mxdMap,v2,logFile)
                statement = "Finished creating Web Service for %s " %v2
                print statement
                logHRRR.main(logFile,statement)
                #upate the service to have a minimum instance of 0
            except Exception as e:
                statement = "Error publishing Web Service for %s . %s" %(v2,e)
                print statement
                logHRRR.main(logFile,statement)
                
                print e
                pass
            #upate the service to have a minimum instance of 0
            print "Back from publishing services"
            mxd = removeAllLayers(mxd)
        #if the variable is not a bin variable
        else :
            #loop through flight levels
            for fint in flightList:
                f = str(fint)
                mxd = removeAllLayers(mxd)
                df = arcpy.mapping.ListDataFrames(mxd, "Layers")[0]
                GL = arcpy.mapping.ListLayers(mxd, "", df)[0]
                addLayer = arcpy.mapping.Layer(dataInput)
                expression = '"FLevel" = %s' %f
                count = getCount(dataInput,addLayer,expression)
                print "HERE  count at flight level %s %s" %(f,count)
                #if count >=1 :   
                #tList = unique_values(addLayer,fieldname,f)
                i = 0
                #for t in tList:
                t = 0
                while t<19:
                    #expt ='"DateTime" = ' + "'%s'" %(t)
                    timeStep = lines[t+4]
                    expt = '"Timestep" = %s' %(t)
                    expt2 = '"FLevel" = %s' %(f)
                    #expression = expt + " AND " + expt2
                    expression = expt2 + " AND " + expt
                    print expression
                    count = getCount(dataInput,addLayer,expression)
                    print "Here count %s" %count
                    if count > 0 :
                        addLayer = arcpy.mapping.Layer(dataInput)
                        addLayer.definitionQuery = None
                        arcpy.ApplySymbologyFromLayer_management(addLayer, layerFile)
                        # Change Layer Names
                        #print str(timeStep)
                        newName = varName + str(timeStep)
                        addLayer.name = newName
                        addLayer.definitionQuery = expression
                                    
                                    
                        if (i == 0) :
                            addLayer.visible = True
                        else :
                            addLayer.visible = False
                        arcpy.mapping.AddLayerToGroup(df, GL, addLayer, "BOTTOM")
                        i = i + 1
                    else :
                        addBlankLayer = addPlaceHolder(timeStep)
                        arcpy.ApplySymbologyFromLayer_management(addBlankLayer, layerBlankFile)
                        arcpy.mapping.AddLayerToGroup(df, GL, addBlankLayer, "BOTTOM")
                        print "adding layer %s" %addBlankLayer.name
                    t=t+1

                                        
                mxdMap = mxdcopy + "_" + f + ".mxd"
                print mxdMap
                v2 = v +"_"+f
                arcpy.RefreshTOC()
                arcpy.RefreshActiveView()

                # Save Group Layer and Map
                mxd.saveACopy(mxdMap)
                print 'Saving to %s' %mxdMap
                try:
                    statement = "Starting to publish map service for " + v2
                    logHRRR.main(logFile,statement)
                    cofps_webService.main(mxdMap,v2,logFile)
                    statement = "Finished publishing map service for %s . Starting Web 2" %v2
                    logHRRR.main(logFile,statement)
                    print "Back from publishing services"
                    print "Going into publishing to cofps-web2"
                    time.sleep(5)
                    cofps_webService2.main(mxdcopy,v,logFile)
                    statement = "Finished publishing second map service for " + v
                    time.sleep(5)
                    logHRRR.main(logFile,statement)
                    print "Back from publishing services"                    #upate the service to have a minimum instance of 0
                except Exception as e:
                    statement = "Problem publishing map service for %s  : %s" %(v2,e)
                    print statement
                    logHRRR.main(logFile,statement)
                    #print "error publishing moving on to next"
                    #print e
                    pass

                print "Back from publishing services"

                mxd = removeAllLayers(mxd)
                                         
            
                            
                
        

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
    tic = time.time()
    args = sys.argv
    log = args[1]
    tempMap = args[2]
    dataInput = args[3]
    layerFile = args[4]
    mxdcopy = args[5]
    varName = args[6]
    extension = args[7]
    log = args[8]
    v = args[8]
    main(log,tempMap,dataInput,layerFile,mxdcopy,varName,extension,v,log)

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
