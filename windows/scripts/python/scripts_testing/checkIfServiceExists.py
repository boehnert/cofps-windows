# Demonstrates how to modify the min and max instances for a service. 
#
# Taken from:
#
# http://server.arcgis.com/en/server/latest/administer/linux/example-edit-service-properties.htm
#
# Note: changed all the interactive prompts to use hard-wired values from the
# imported COFPS_config module, and use httplib.HTTPSConnection instead of
# httplib.HTTPConnection.
#
# Jennifer Boehnert 9/12/2017

# For Http calls
import httplib, urllib, json

# For system tools
import sys, datetime

# For reading passwords without echoing
import getpass

import COFPS_config as cf
import time

# Defines the entry point into the script
def main(serviceName):
    # Print some info
    print
    print "This tool is a sample script that detects if services exists in a folder."
    print  
    
    # Ask for admin/publisher user name and password
    username = cf.Ags_usr
    password = cf.Ags_pwd
    
    # Ask for server name
    serverName = cf.Ags_host
    serverPort = cf.Ags_mgt_port

    service = serviceName
    print service

    # Create a list to hold stopped services
    stoppedList = []
    
    # Get a token
    token = getToken(username, password, serverName, serverPort)
    if token == "":
        print "Could not generate a token with the username and password provided."
        return
    
   
    folder = "ROOT/"
            
    folderURL = "/arcgis/admin/services/" + folder
    serviceURL = "/arcgis/admin/services/" + service

    print token    
    # This request only needs the token and the response formatting parameter 
    params = urllib.urlencode({'token': token, 'f': 'json'})
    
    headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
    
    # Connect to URL and post parameters    
    httpConn = httplib.HTTPConnection(serverName, serverPort)
    httpConn.request("POST", folderURL, params, headers)
    
    # Read response
    response = httpConn.getresponse()
    if (response.status != 200):
        httpConn.close()
        print "Could not read folder information."
        return
    else:
        data = response.read()
        
        # Check that data returned is not an error object
        if not assertJsonSuccess(data):          
            print "Error when reading folder information. " + str(data)
        else:
            print "Processed folder information successfully. Now processing services..."

        # Deserialize response into Python object
        dataObj = json.loads(data)
        httpConn.close()

        # Loop through each service in the folder and stop or start it    
        for item in dataObj['services']:

            fullSvcName = item['serviceName'] + "." + item['type']

            print "Reading service name %s " %fullSvcName

##            # Construct URL to stop or start service, then make the request                
##            statusURL = "/arcgis/admin/services/" + folder + fullSvcName + "/status"
##            httpConn.request("POST", statusURL, params, headers)
##            
##            # Read status response
##            statusResponse = httpConn.getresponse()
##            if (statusResponse.status != 200):
##                httpConn.close()
##                print "Error while checking status for " + fullSvcName
##                return
##            else:
##                statusData = statusResponse.read()
##                              
##                # Check that data returned is not an error object
##                if not assertJsonSuccess(statusData):
##                    print "Error returned when retrieving status information for " + fullSvcName + "."
##                    print str(statusData)
##
##                else:
##                    # Add the stopped service and the current time to a list
##                    statusDataObj = json.loads(statusData)
##                    if statusDataObj['realTimeState'] == "STOPPED":
##                        stoppedList.append([fullSvcName,str(datetime.datetime.now())])
##                                  
##            httpConn.close()           
##
##    # Check number of stopped services found
##    if len(stoppedList) == 0:
##        print "No stopped services detected in folder " + folder.rstrip("/")
##    else:
##        # Write out all the stopped services found
##        # This could alternatively be written to an e-mail or a log file
##        for item in stoppedList:
##            print "Service " + item[0] + " was detected to be stopped at " + item[1]    
##
    return


# A function to generate a token given username, password and the adminURL.
def getToken(username, password, server, port):
    print "Getting token"
    # Token URL is typically http://server[:port]/arcgis/admin/generateToken
    token_url = "/arcgis/admin/generateToken"
    
    params = urllib.urlencode({'username': username, 'password': password, 'client': 'requestip', 'f': 'json'})
    
    resp_json = post_ags_json_request(token_url, params, server, port)
    if resp_json:
        return resp_json["token"]
    else:
        return
    
def post_ags_json_request(url, params, server, port):
    if 'f=json' not in params:
        params += '&f=json' if params else 'f=json'

    headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
    
    #http://stackoverflow.com/questions/5319430/how-do-i-have-python-httplib-accept-untrusted-certs
    http_conn = httplib.HTTPSConnection(server, port)
    http_conn.request("POST", url, params, headers)
    
    response = http_conn.getresponse()
    if (response.status != 200):
        http_conn.close()
        print "Error requesting: %s, %s, %s, %d" % (url,params,server,port)
        return None
    else:
        data = response.read()
        http_conn.close()
        
        # Check that data returned is not an error object
        if not assertJsonSuccess(data):            
            return None
        
    return json.loads(data)

def get_ags_json_request(url, params, server, port):
    if 'f=json' not in params:
        params += '&f=json' if params else 'f=json'
    
    #http://stackoverflow.com/questions/5319430/how-do-i-have-python-httplib-accept-untrusted-certs
    http_conn = httplib.HTTPSConnection(server, port)
    http_conn.request("GET", "%s?%s" % (url,params))
    
    response = http_conn.getresponse()
    if (response.status != 200):
        http_conn.close()
        print "Error requesting: %s, %s, %s, %d" % (url,params,server,port)
        return None
    else:
        data = response.read()
        http_conn.close()
        if not assertJsonSuccess(data):            
            return None
        
    return json.loads(data)

# A function that checks that the input JSON object 
#  is not an error object.
def assertJsonSuccess(data):
    obj = json.loads(data)
    if 'status' in obj and obj['status'] == "error":
        print "Error: JSON object returns an error. " + str(obj)
        return False
    else:
        return True
    
        
# Script start
if __name__ == "__main__":
    args = sys.argv
    serviceName = args[1]
    
    main(serviceName)
