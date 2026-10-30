import sys,os
import json
import string
import traceback
from optparse import OptionParser
import requests
import glob
import urllib3
import subprocess
import datetime



def is_valid_json(myjson):
    try:
        json_object = json.loads(myjson)
    except ValueError as e:
        return False
    return True



def run_performance_test(selected_api, api_grp, config_obj, server): 

    base_api_url = config_obj["base_url"][server]
    log_dir = config_obj["data_path"] + "/logs/"
 
    last_id_api_url = base_api_url + "/misc/lastid"
 

    user_name = os.getlogin()
    file_list = glob.glob("performance/*.json")
    if api_grp != "all":
        file_list = glob.glob("performance/%s.json" % (api_grp))

   
    file_list = sorted(file_list)

    out_obj_list = []
    last_list_id = ""
    try:
        for in_file in file_list:
            if is_valid_json(open(in_file, "r").read()) == False:
                res_obj = {"infile":in_file, "error_code": "invalid-query-json"}
                print (json.dumps(res_obj, indent=4))
                continue
            t_obj_dict = json.loads(open(in_file, "r").read())
            list_id = ""
            api_name_list = list(t_obj_dict.keys()) if selected_api == "" else [selected_api]
            for api_name in api_name_list:
                t_obj = t_obj_dict[api_name]
                t_obj["url"] += "/" if t_obj["url"][-1] != "/" else ""
                api_url = base_api_url + t_obj["url"]
                req_obj_list = []
                if "querylist" in t_obj:
                    for o in t_obj["querylist"]:
                        if api_name.find("_list") != -1 and "id" in o["query"]:
                            o["query"]["id"] = last_list_id
                        req_obj_list.append(o["query"])
                elif "query" in t_obj:
                    if api_name.find("_list") != -1 and "id" in t_obj["query"]:
                        t_obj["query"]["id"] = last_list_id
                    req_obj_list.append(t_obj["query"])
                idx = 0
                for req_obj in req_obj_list:
                    idx += 1
                    o = {
                        "name":api_name, "query":req_obj, 
                        "bad_respose":False, "semantic":False,
                    }
                    semantic_qlist = []
                    if "semantic" in t_obj:
                        o["semantic"] = True
                        o.pop("query")
                        semantic_qlist = t_obj["query"].split("|")
                        req_obj = {}
                    
                    if api_url.find("/list/") != -1:
                        req_obj["id"] = list_id
                    if semantic_qlist == []:
                        ts_start = datetime.datetime.now()
                        res = requests.post(api_url, json=req_obj, verify=False)
                        #res = requests.get(api_url, json=req_obj, verify=False)
                        ts_end = datetime.datetime.now()
                        diff = (ts_end - ts_start).total_seconds()
                        print (diff, res.status_code, api_name)
                        if res.status_code == 200:
                            res_obj = json.loads(res.content)
                            if "list_id" in res_obj:
                                list_id = res_obj["list_id"]
                    else:
                        for q in semantic_qlist:
                            url = api_url + q + "/"
                            ts_start = datetime.datetime.now()
                            res = requests.post(url, json={}, verify=False)
                            #res = requests.get(url, json={}, verify=False)
                            ts_end = datetime.datetime.now()
                            diff = (ts_end - ts_start).total_seconds()
                            print (diff, res.status_code, api_name, q)



    except Exception as e:
        print (traceback.format_exc())

    return

