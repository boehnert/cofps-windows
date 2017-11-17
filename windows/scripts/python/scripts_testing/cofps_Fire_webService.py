

#This script is used to publish fire map services
# called from createMap.py
# example cofps_Fire_webService.main(mxdcopy,v,logFile)

#/*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*
# * Copyright (c) 2016 UCAR
# * University Corporation for Atmospheric Research(UCAR)
# * National Center for Atmospheric Research(NCAR)
# * Research Applications Program(RAP)
# * P.O.Box 3000, Boulder, Colorado, 80307-3000, USA
# * All rights reserved. Licenced use only.
# * $Date: 2017-09-20
# *=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*/


# Import system modules
import arcpy, traceback, os
from arcpy import env
import time
import deleteMapService
import sys

import xml.dom.minidom as DOM

# Check out any necessary licenses
arcpy.CheckOutExtension("spatial")
arcpy.env.overwriteOutput = True


try:

    def main(mxdName,service,summary, tags):
	
        start = time.ctime()
        try:
            print "About to delete service %s" %service
            serviceID = service.split("_")[-2]
            print "serviceID %s" %serviceID
            
            #delete_mapservice.main(serviceID)
            #deleteMapService.main(service)
                            
            print "Back from deleting service"
        except:
            print "There was an error deleting the map service.  We will continue and try to publish it"
            
            

         # Set environment settings
        env.workspace = r"E:\cofireop"
        # define local variables
        wrkspc = r"E:\cofireop\Mapping"
        mapDoc = arcpy.mapping.MapDocument(mxdName)


        out_name = "arcgis on cofps-web1_6443 (publisher).ags"
        con = os.path.join(wrkspc,out_name)

        sddraft = wrkspc + os.sep + service + '.sddraft'
        sd = wrkspc +os.sep+ service + '.sd'
        #remove old SD file
        #print "checking if file exist %s" %sd
        if os.path.exists(sd):
            #print "it exists....deleting now"
            os.remove(sd)
            #time.sleep(5)

        # create service definition draft
        arcpy.mapping.CreateMapSDDraft(mapDoc, sddraft, service, 'ARCGIS_SERVER',
                                                      con, True, None, summary, tags)

        # Analyze the service definition draft
        analyzeSD = arcpy.mapping.AnalyzeForSD(sddraft)

        # Print errors, warnings, and messages returned from the analysis
        #print "The following information was returned during analysis of the MXD:"
        
        for key in ('messages', 'warnings', 'errors'):
            #print '----' + key.upper() + '---'
            vars = analyzeSD[key]
            for ((message, code), layerlist) in vars.iteritems():
                #print '    ', message, ' (CODE %i)' % code
                #print '       applies to:',
                for layer in layerlist:
                    print layer.name,
                print

        # Stage and upload the service if the sddraft analysis did not contain errors
        if analyzeSD['errors'] == {}:
            # Execute StageService. This creates the service definition.
            arcpy.StageService_server(sddraft, sd)
            try :
                # Execute UploadServiceDefinition. This uploads the service definition and publishes the service.
                arcpy.UploadServiceDefinition_server(sd, con, "", "", "EXISTING")
                print "Service successfully published"
            except :
                print "ERROR Happenned when publishing the map service moving on the next map service"
                return False
        return True
                       


    if __name__ == '__main__':
        args = sys.argv
        # FGRNHFXList,ROSList
        mxdName = args[1]
        serviceName = args[2]
        summary = args[3]
        tags = args[4]
        main(mxdName,serviceName,summary, tags)

except :
    print "ERROR Happenned"
     # Get the traceback object
    tb = sys.exc_info()[2]
    tbinfo = traceback.format_tb(tb)[0]

    # Concatenate information together concerning the error into a message string
    pymsg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n" + str(sys.exc_info()[1])
    msgs = "ArcPy ERRORS:\n" + arcpy.GetMessages(2) + "\n"

    

