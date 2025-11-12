import os,sys
import string
import glob
import json
import datetime
import time
import pytz
import requests


###############################
def main():


    api_grp = "search"
    query_dict = json.load(open("performance/queries/%s.json" % (api_grp)))    
    #record_type_list = ["glycan"]
    record_type_list = list(query_dict.keys())
    for record_type in record_type_list:
        api_url = "http://localhost:8082/%s/%s/" % (record_type, api_grp)
        for obj in query_dict[record_type]:
            lbl, req_obj, prf_status = obj["lbl"], obj["query"], obj["status"]
            if req_obj == {}:
                continue
            #if prf_status == 1:
            #    continue
            start_ts = datetime.datetime.now(pytz.timezone('US/Eastern'))
            res = requests.post(api_url, json=req_obj, verify=False)
            end_ts = datetime.datetime.now(pytz.timezone('US/Eastern'))
            res_obj = json.loads(res.content)
            if res.status_code != 200:
                print (res_obj)
                continue
            res_obj = json.loads(res.content)
            size = len(res.content)
            diff = end_ts - start_ts
            print ("%s,%s,%s,%s" % (prf_status, diff, lbl, record_type))
            #print (json.dumps(res_obj, indent=4))
            #print ("//\n") 
            time.sleep(2) 





if __name__ == '__main__':
    main()
