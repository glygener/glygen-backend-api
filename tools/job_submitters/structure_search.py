#!/bin/env python
import os
import sys
import json
import time
import requests
from optparse import OptionParser





class APIFrameworkClient:

    class APISubmitError(RuntimeError):
        pass

    class APIUnfinishedError(RuntimeError):
        pass



    def __init__(self,**kwargs):
        #self._apiurl= kwargs.get('apiurl',self.apiurl)
        self._email = kwargs.get('developer_email',self.developer_email)
        self._nocache = kwargs.get('nocache',self.nocache)
        self._max_retry = kwargs.get('max_request_retry',3)
        self._interval = kwargs.get('request_interval',1)
        self._max_retry_for_unfinished_task = kwargs.get('max_retrieve_wait',self.max_retrieve_wait)

    def request(self, sub, params, api_url):
        for i in range(self._max_retry):
            try:
                #response = requests.post(self._apiurl + "/" + sub, params)
                response = requests.post(api_url + "/" + sub, params)
                return response
            except:
                pass
            time.sleep(self._interval)

    def retrieve(self, task_id, api_url):
        for i in range(self._max_retry_for_unfinished_task):
            time.sleep(self._interval)
            try:
                res = self.retrieve_once(task_id, api_url)
                return res
            except APIFrameworkClient.APIUnfinishedError:
                continue
        raise APIFrameworkClient.APIUnfinishedError("The task %s is not finished yet" % task_id)

    def get(self, **kwargs):
        api_url = kwargs["api_url"]
        task_id = self.submit(kwargs, api_url)
        if task_id == -1:
            return {"error":["container is not running!"], "status":-1}

        resjson = self.retrieve(task_id, api_url)
        return resjson

    def submit(self, task, api_url):
        param = {"task": json.dumps(task), "developer_email": self._email}
        if self.nocache:
            param["nocache"] = 'true'
        res1 = self.request("submit", param, api_url)
        if res1 == None:
            return -1
        submit_result = res1.json()
        try:
            task_id = submit_result[0][u"id"]
            return task_id
        except TypeError:
            pass
        raise APIFrameworkClient.APISubmitError(submit_result)

    def retrieve_once(self, task_id, api_url):
        param = {"task_id": task_id }
        try:
            res2 = self.request("retrieve", param, api_url)
            res2json = res2.json()[0]
        except:
            raise
        if not res2json[u"finished"]:
            raise APIFrameworkClient.APIUnfinishedError("The task %s is not finished yet" % task_id)
        return res2json

class SubstructureSearch(APIFrameworkClient):
    developer_email='rykahsay@gwu.edu'
    nocache = False
    max_retrieve_wait = 120 # wait up to 2 minutes for result



if __name__ == '__main__':

    usage = "\n%prog  [options]"
    parser = OptionParser(usage,version="%prog version___")
    parser.add_option("-i","--infile",action="store",dest="infile",help="Input file")
    parser.add_option("-o","--outfile",action="store",dest="outfile",help="Output file")
    parser.add_option("-u","--apiurl",action="store",dest="apiurl",help="API URL")
     
    (options,args) = parser.parse_args()
    for key in ([options.infile, options.outfile, options.apiurl]):
        if not (key):
            parser.print_help()
            sys.exit(0)
    
    in_file = options.infile
    out_file = options.outfile
    api_url = options.apiurl

    #api_url = 'http://running_substructure:10980'


    task = json.loads(open(in_file).read())
    task["api_url"] = api_url

    align = task.get('align','substructure')
    substr = SubstructureSearch()


    res = {}
    try:
        res = substr.get(**task)
    except SubstructureSearch.APIUnfinishedError:
        res["error"] = "Did not complete"


    for key in ("finished","stat","id"):
        if key in res:
            del res[key]
    if res["status"] == "OK":
        res["result"] = res["result"][align]
        if "error" in res:
            del res["error"]
    else:
        if "result" in res:
            del res["result"]  


    with open(out_file, "w") as FW:
        FW.write("%s\n" % (json.dumps(res, indent=4, sort_keys=True)))
        #print(json.dumps(res[align], indent=4, sort_keys=True))
    
    if "error" in res:
        print(res["error"][0])
        sys.exit(1)



