import urllib3
urllib3.disable_warnings()
import requests;
import json
import os;
auth=(os.environ.get('user'),os.environ.get('password'))
def escape(s):
    url=s.replace("/","_").replace(":","_").replace("?","_").replace("&","_").replace("=","_")
    return url;
cache_path="/users/kor/temp"

class Requestor:
    def lookupInCache(self,url):
        cpath=cache_path+"/"+escape(url);
        if (os.path.isfile(cpath)):
            with open(cpath) as handle:
                r= json.load(handle);
                print "Cached:"+url;
                return r;
        return None;

    def storeInCache(self,url,data):
        cpath=cache_path+"/"+escape(url);
        with open(cpath,"w") as handle:
          json.dump(data,handle);


    def get(self,url,params={},auth=auth):
        c=self.lookupInCache(url);
        if c!=None:
            return c;
        rs=requests.get(url,params=params,auth=auth);
        if rs.status_code==401:
            return { "url":url}
        if (rs.status_code>210):
            raise IOError("Error")
        js=json.JSONDecoder().decode(rs.text);
        self.storeInCache(url,js);
        return js

    def readCollection(self,url,params={}):
        res=[]
        params['state']='all'
        c=self.lookupInCache(url);
        if c!=None:
           return c;
        ourl=url;
        while True:
            rs=requests.get(url,params=params,auth=auth);
            js=json.JSONDecoder().decode(rs.text);
            if (rs.status_code>210):
                raise IOError("Error")
            res+=js;
            if 'next' in rs.links:
                url=rs.links['next']['url'];
            else:
                break;
            print len(res);
        self.storeInCache(ourl,res);
        return res;
