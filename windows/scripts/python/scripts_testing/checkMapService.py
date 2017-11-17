#!/usr/bin/env python

import urllib
import httplib
import json
import sys
import optparse
import datetime
import os
import glob
#import log_msg

import COFPS_config

user = COFPS_config.Ags_usr
passwd = COFPS_config.Ags_pwd
server = COFPS_config.Ags_host
port = 6443

"""
Script removes all ArcGIS Server map services containing the simid in the name

Example Usage: delete_mapservice.py 581782f2c9e77c003791331d
"""
#this procedure will look for directories for the services
def findProductList(uKey, service):
    pathname = r"E:\cofireop\sim\gisdata"
    dirList = []
    toDelete = []
    found = 0
    ran = 0
    #print "uKey = %s" %uKey
    dirList.append("First")
    for dirName, subdirList, fileList in os.walk(pathname):
        dirKey = dirName.split("\\")[-1]
        
        if dirKey == uKey :
            stversions = dirName.split("\\")[-3]
            #print stversions
            if (stversions != ".stversions") :
                for dirs in dirList :
                    ran = 1
                    if dirs == dirName :  #this directory has already been rerun
                        found = 1
                    if found == 0 :  #the directory is unique and has not been run yet
                        #print "dirs %s and dirName = %s" %(dirs,dirName)
                        dirList.append(dirName)
                        print "found it %s for service" %(dirName,service)
                        #run the code to rerun the publications
                        productList = os.path.join(dirName,"product_list.txt")
                        return
    if ran == 0 :        
        print "To Delete %s for the service %s" %(dirName, service)
        

               
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

 
def get_token(username, password, server, port):
    print "Getting token"
    # Token URL is typically http://server[:port]/arcgis/admin/generateToken
    token_url = "/arcgis/admin/generateToken"
    
    params = urllib.urlencode({'username': username, 'password': password, 'client': 'requestip', 'f': 'json'})
    
    resp_json = post_ags_json_request(token_url, params, server, port)
    
    if resp_json:
        return resp_json["token"]
    else:
        return None


def get_service_names(server, port):
    print "Getting map service names"
    resp_json = get_ags_json_request('/arcgis/rest/services', "", server, port)
    if resp_json:
        return map(lambda d: d['name'], resp_json['services'])
    else:
        return None


# A function that checks that the input JSON object 
#  is not an error object.  
def assertJsonSuccess(data):
    obj = json.loads(data)
    if 'status' in obj and obj['status'] == "error":
        print "Error: JSON object returns an error. " + str(obj)
        return False
    else:
        return True

def main(serviceName) :
    
    token = get_token(user, passwd, server, port)
    if not token:
        print "Unable to acquire ArcGIS token"
        sys.exit(1)
    else :
        checkMapService(serviceName,token,server,port)

       

def checkMapService(name, token, server, port):
    # Create a list to hold stopped services
    stoppedList = []
    brokenList = []
    
    folder = "ROOT"
     # Construct URL to read folder
    if str.upper(folder) == "ROOT":
        folder = ""
    else:
        folder += "/"
            
    folderURL = "/arcgis/admin/services/" + folder      
    serviceURL = "/arcgis/admin/services/" + name
    params = urllib.urlencode({'token':token,'f': 'json'})
    print "going in"
    dataObj = post_ags_json_request(folderURL, params, server, port)
    print "Back from post"

    # Loop through each service in the folder and stop or start it    
    for item in dataObj['services']:

        fullSvcName = item['serviceName'] + "." + item['type']

        # Construct URL to stop or start service, then make the request                
        statusURL = "/arcgis/admin/services/" + folder + fullSvcName + "/status"
        dataObj = post_ags_json_request(statusURL, params, server, port)
        
        try :
            if dataObj['realTimeState'] == "STOPPED":
                stoppedList.append([fullSvcName,str(datetime.datetime.now())])
        except Exception as e:
            print "Error triggered in the main call"
            brokenList.append([fullSvcName,str(datetime.datetime.now())])
                              
                   

    # Check number of stopped services found
    if len(stoppedList) == 0:
        print "No stopped services detected in folder " + folder.rstrip("/")
    else:
        # Write out all the stopped services found
        # This could alternatively be written to an e-mail or a log file
        for item in stoppedList:
            #get unique key
            serviceBits = item[0].split("_")
            if (len(serviceBits) == 3) or serviceBits[0] == "Fire" :
                uKey = serviceBits[-2]
                print "Service " + item[0] + " was detected "
                findProductList(uKey,item[0])

    if len(brokenList) == 0:
        print "No stopped services detected in folder " + folder.rstrip("/")
    else:
        # Write out all the stopped services found
        # This could alternatively be written to an e-mail or a log file
        for item in brokenList:
            print "Service " + item[0] + " was BROKEN at " + item[1]    



    return


if __name__ == '__main__':
    
    args = sys.argv
    sim_id = args[1]
    
    main(sim_id)

    
    
