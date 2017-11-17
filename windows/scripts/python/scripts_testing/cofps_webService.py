
#This script is used to publish HRRR map services
# called from HRRR_images.py
# example status = cofps_webService.main(mxdcopy,serviceName,summary,tags)
#returns status

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

import xml.dom.minidom as DOM
import updateMinMaxInstances
import logHRRR
import deleteMapService
import time
# Check out any necessary licenses
arcpy.CheckOutExtension("spatial")
arcpy.env.overwriteOutput = True


try:

    def main(mxdName,v,logFile):
        # Set environment settings
        env.workspace = r"E:\cofireop"
        # define local variables
        wrkspc = r"E:\cofireop\Mapping"
        mapDir = r"E:\cofireop\Mapping\HRRRMaps"
       
        print v
        service = 'HRRR_%s_Current' %v
        print "*******************"
        print "Deleting service name is %s" %service
        print "*******************"
          
        summary = '%s from HRRR' %v
        tags = v
        mapDoc = arcpy.mapping.MapDocument(mxdName)

        out_name = "arcgis on cofps-web1_6443 (publisher).ags"
        con = os.path.join(wrkspc,out_name)
        sddraft = wrkspc + os.sep + service + '.sddraft'
        sd = wrkspc +os.sep+ service + '.sd'

        #remove the SD file if it already exists
        if os.path.exists(sd):
            os.remove(sd)
            
        # create service definition draft
        statement = "Creating SDDraft for %s" %v
        print statement
        logHRRR.main(logFile,statement)
        arcpy.mapping.CreateMapSDDraft(mapDoc, sddraft, service, 'ARCGIS_SERVER',
                                                  con, False, None, summary, tags)

        statement = "Done %s" %v
        print statement
        logHRRR.main(logFile,statement)

        # Analyze the service definition draft
        analyzeSD = arcpy.mapping.AnalyzeForSD(sddraft)

        # Print errors, warnings, and messages returned from the analysis
        print "The following information was returned during analysis of the MXD:"
        try:
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

                # Execute UploadServiceDefinition. This uploads the service definition and publishes the service.
                arcpy.UploadServiceDefinition_server(sd, con, "", "", "EXISTING")
                print "Service successfully published"
                statement = "Service Create successfully for %s" %v
                print statement
                logHRRR.main(logFile,statement)
            else:
                statement = "Service could not be published because errors were found during analysis for %s" %v
                print statement
                logHRRR.main(logFile,statement)
                print "Service could not be published because errors were found during analysis."
                return False
            return True
        
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

            print "-----We have a problem------"
            print "Trying to delete service again"
            time.sleep(10)
            deleteMapService.main(service)
            return False
           

    if __name__ == '__main__':
        args = sys.argv
        mxdName = args[1]
        variable = args[2]
        log = args[3]
        main(mxdName,variable,log)

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

