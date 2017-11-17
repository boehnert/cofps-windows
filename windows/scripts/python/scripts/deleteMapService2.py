#!/usr/bin/env python

import urllib
import httplib
import json
import sys
import optparse
#import log_msg

import COFPS_config

user = COFPS_config.Ags_usr
passwd = COFPS_config.Ags_pwd
server = COFPS_config.Ags_host2
port = 6443

"""
Script removes all ArcGIS Server map services containing the simid in the name

Example Usage: delete_mapservice.py 581782f2c9e77c003791331d
"""

def post_ags_json_request(url, params, server, port):
    if 'f=json' not in params:
        params += '&f=json' if params else 'f=json'

    headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
    print "in post"
    #http://stackoverflow.com/questions/5319430/how-do-i-have-python-httplib-accept-untrusted-certs
    http_conn = httplib.HTTPSConnection(server, port)
    print "server = %s and port = %s" %(server, port)
    http_conn.request("POST", url, params, headers)
    print "done with con"
    
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
    print "token url %s" %token_url
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
    #token = get_token(user, passwd, server, port)
    #token = "None"
    #print "back"
    #if not token:
    #    print "Unable to acquire ArcGIS token"
    #    sys.exit(1)

     #   print "Removing %d map services" % len(serviceName)
       
        #deleteMapService(serviceName,token,server,port)
    deleteMapService(serviceName,None,server,port)

        #check that the map service was deleted
        #serviceList = arcpy.mapping.ListMapServices("http://bond/arcgis/services","bond")
        #for serviceName in serviceList:
        #    print serviceName

    


def deleteMapService(name, token, server, port):
    print "Removing service %s" % name
    delete_url = "/arcgis/admin/services/%s.MapServer/delete" % name
    
    params = urllib.urlencode({'token':token,'f': 'json'})
    
    resp_json = post_ags_json_request(delete_url, params, server, port)
    print resp_json


if __name__ == '__main__':
    

    sim_id = args[0]
    assert len(sim_id) == 24, "Check that you are using a valid simid"
    main(sim_id)

    
    
