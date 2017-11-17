#!/usr/bin/env python

import urllib
import httplib
import json
import sys
import optparse
#import log_msg

import COFPS_config
import ssl

#try:
#    _create_unverified_https_context = ssl._create_unverified_context
#except AttributeError:
    # Legacy Python that doesn't verify HTTPS certificates by default
#    pass
#else:
    # Handle target environment that doesn't support HTTPS verification
#    ssl._create_default_https_context = _create_unverified_https_context




user = COFPS_config.Ags_usr
passwd = COFPS_config.Ags_pwd
server = COFPS_config.Ags_host
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
    token = get_token(user, passwd, server, port)
    
    print token
    if not token:
        print "Unable to acquire ArcGIS token"
        sys.exit(1)

     #   print "Removing %d map services" % len(serviceName)
       
    #deleteMapService(serviceName,token,server,port)
    restartMapService(serviceName,None,server,port)


def restartMapService(name, token, server, port):
    print "Restarting service %s" % name
    delete_url = "/arcgis/admin/services/%s.MapServer/status" % name
    print delete_url
    #stopOrStartURL = "/arcgis/admin/services/" + folder + fullSvcName + "/" + stopOrStart
    
    params = urllib.urlencode({'token':token,'f': 'json'})
    
    resp_json = post_ags_json_request(delete_url, params, server, port)
    if resp_json['realTimeState'] == "STOPPED":
        print "it is stopped"
    else:
        print "it is started"


if __name__ == '__main__':
    

    sim_id = args[0]
    main(sim_id)

    
    
