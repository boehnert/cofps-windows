#!/usr/bin/env python

import urllib
import httplib
import json
#import log_msg

#Code to deal with SSL certificate failed issue
#Origin: https://github.com/khibma/ArcGISAdministrationToolkit/tree/master/CommandLine
import ssl

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    # Legacy Python that doesn't verify HTTPS certificates by default
    pass
else:
    # Handle target environment that doesn't support HTTPS verification
    ssl._create_default_https_context = _create_unverified_https_context


"""
Script provides reusable arcgis server http connection functions.
"""

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
    
    # Token URL is typically http://server[:port]/arcgis/admin/generateToken
    token_url = "/arcgis/admin/generateToken"
    
    params = urllib.urlencode({'username': username, 'password': password, 'client': 'requestip', 'f': 'json'})
    
    resp_json = post_ags_json_request(token_url, params, server, port)
    if resp_json:
        return resp_json["token"]
    else:
        return None


def get_service_names(server, port):
    
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

def stop_mapservice(name, token, server, port):
    
    stop_url = "/arcgis/admin/services/%s.MapServer/stop" % name
   
    
    params = urllib.urlencode({'token':token,'f': 'json'})
    resp_json = post_ags_json_request(stop_url, params, server, port)
    print resp_json
    
    return resp_json['status'] != 'error'

def start_mapservice(name, token, server, port):
    
    start_url = "/arcgis/admin/services/%s.MapServer/start" % name
    
    params = urllib.urlencode({'token':token,'f': 'json'})
    
    resp_json = post_ags_json_request(start_url, params, server, port)
    print resp_json
    return resp_json['status'] != 'error'

def delete_mapservice(name, token, server, port):
    
    stop_url = "/arcgis/admin/services/%s.MapServer/stop" % name
    start_url = "/arcgis/admin/services/%s.MapServer/start" % name
    
    params = urllib.urlencode({'token':token,'f': 'json'})
    resp_json = post_ags_json_request(stop_url, params, server, port)
    print resp_json
    resp_json = post_ags_json_request(start_url, params, server, port)
    print resp_json
    return resp_json['status'] != 'error'


def get_mapservice_sims(user, passwd, server, port):
    token = get_token(user, passwd, server, port)
    if not token:
        sys.exit(1)

    service_names = get_service_names(server,port)
    if not service_names:
        sys.exit(1)

    simids = set([])
    for name in service_names:
        splits = name.split('_')
        if len(splits) > 1 and len(splits[1]) == 24:
            simids.add(splits[1])

    return sorted(list(simids))
