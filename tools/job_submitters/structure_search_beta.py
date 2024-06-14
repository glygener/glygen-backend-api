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


    #apiurl = 'http://running_substructure:10990'
    apiurl = 'http://172.17.0.1:10980'

    developer_email = None
    max_retrieve_wait = 300
    nocache = False

    def __init__(self,**kwargs):
        self._apiurl= kwargs.get('apiurl',self.apiurl)
        self._email = kwargs.get('developer_email',self.developer_email)
        self._nocache = kwargs.get('nocache',self.nocache)
        self._max_retry = kwargs.get('max_request_retry',3)
        self._interval = kwargs.get('request_interval',1)
        self._max_retry_for_unfinished_task = kwargs.get('max_retrieve_wait',self.max_retrieve_wait)

    def request(self, sub, params):
        for i in range(self._max_retry):
            try:
                response = requests.post(self._apiurl + "/" + sub, params)
                return response
            except:
                pass
            time.sleep(self._interval)

    def retrieve(self, task_id):
        for i in range(self._max_retry_for_unfinished_task):
            time.sleep(self._interval)
            try:
                res = self.retrieve_once(task_id)
                return res
            except APIFrameworkClient.APIUnfinishedError:
                continue
        raise APIFrameworkClient.APIUnfinishedError("The task %s is not finished yet" % task_id)

    def get(self, **kwargs):
        task_id = self.submit(kwargs)
        resjson = self.retrieve(task_id)
        return resjson

    def submit(self, task):
        param = {"task": json.dumps(task), "developer_email": self._email}
        if self.nocache:
            param["nocache"] = 'true'
        res1 = self.request("submit", param)
        submit_result = res1.json()
        try:
            task_id = submit_result[0][u"id"]
            return task_id
        except TypeError:
            pass
        raise APIFrameworkClient.APISubmitError(submit_result)

    def retrieve_once(self, task_id):
        param = {"task_id": task_id }
        try:
            res2 = self.request("retrieve", param)
            res2json = res2.json()[0]
        except:
            raise
        if not res2json[u"finished"]:
            raise APIFrameworkClient.APIUnfinishedError("The task %s is not finished yet" % task_id)
        return res2json

class SubstructureSearch(APIFrameworkClient):
    
    #apiurl = 'http://running_substructure_beta:10990'
    apiurl = 'http://172.17.0.1:10980'
    developer_email='rykahsay@gwu.edu'
    # nocache = True
    max_retrieve_wait = 120 # wait up to 2 minutes for result



if __name__ == '__main__':

    usage = "\n%prog  [options]"
    parser = OptionParser(usage,version="%prog version___")
    parser.add_option("-i","--infile",action="store",dest="infile",help="Input file")
    parser.add_option("-o","--outfile",action="store",dest="outfile",help="Output file")
    
    (options,args) = parser.parse_args()
    for key in ([options.infile, options.outfile]):
        if not (key):
            parser.print_help()
            sys.exit(0)
                                                                                    
    in_file = options.infile
    out_file = options.outfile
    task = json.loads(open(in_file).read())

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



