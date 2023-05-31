import sys,os
import json
import string
import traceback
from optparse import OptionParser
from bson import json_util, ObjectId
import requests
import glob
import urllib3
import subprocess

import jsonref
from jsonschema import validate, Draft4Validator

urllib3.disable_warnings()


def is_valid_json(myjson):
    try:
        json_object = json.loads(myjson)
    except ValueError as e:
        return False
    return True



def validate_response(res_obj, schema_file):

    base_uri = 'file://{}/'.format(os.path.dirname(schema_file))
    schema_obj = jsonref.load(open(schema_file, 'r'), base_uri=base_uri, jsonschema=True)
    #resolver = jsonschema.RefResolver(schema_file, None)
    #schema_obj = simplejson.loads(open(schema_file, "r").read())
    #res_obj = simplejson.loads(open(data_file, "r").read())
    v = Draft4Validator(schema_obj)
    error_list = sorted(v.iter_errors(res_obj), key=str)
    res = {"error_list":[]}
    for error in error_list:
        if error.message not in res["error_list"]:
            res["error_list"].append(error.message)

    res["status"] = "passed" if res["error_list"] == [] else "failed"

    return res



def get_id_dict_one(api_url):

    id_dict = {}
    res = requests.post(api_url, json={}, verify=False)
    res_obj = json.loads(res.content)
    for coll in res_obj:
        p = coll[2:]
        id_dict[p] = res_obj[coll]
        if "_id" in id_dict[p]:
            id_dict[p]["id"] = id_dict[p]["_id"]
        
    return id_dict


def get_id_dict_two():

    id_dict = {}
    doc = json.loads(open("queries/listid/listid.json", "r").read())
    for grp in doc:
        id_dict[grp] = {}
        for k in doc[grp]:
            id_dict[grp][k] = doc[grp][k]

    return id_dict



def run_exhaustive(in_file, record_type, config_obj, server):

    user_name = os.getlogin()
    batch_idx = in_file.split(".")[-2]
    log_dir = config_obj["data_path"]  + "/logs/"
    summary_file = log_dir + "%s_test_summary_%s_mode_2.%s.csv" % (user_name, record_type, batch_idx)
    row = ["main_id", "flags"]
    with open(summary_file, "w") as FW:
        FW.write("%s\n" % (",".join(row)))

    main_id_list = json.loads(open(in_file, "r").read())

    for main_id in main_id_list:
        api_url = config_obj["base_url"][server] + "/%s/detail/%s/" % (record_type, main_id)
        req_obj = {}
        if record_type in ["motif"]:
            api_url = config_obj["base_url"][server] + "/%s/detail/" % (record_type)
            req_obj = {"motif_ac":main_id}
        o = {"bad_respose":False, "url":api_url}
        res = requests.get(api_url, json=req_obj, verify=False)
        o["status_code"] = res.status_code
        if is_valid_json(res.content) == False:
            o["bad_respose"] = True
        else:
            res_obj = json.loads(res.content)
            if "error_list" in res_obj:
                o["error_list"] = res_obj["error_list"]
            else:
                schema_file = "../specs/%s/detail/response.schema.json" % (record_type)
                if os.path.isfile(schema_file) == True:
                    o["validation"] = validate_response(res_obj,schema_file)
                else:
                    o["validation"] = {"status":"noschema"}

        flag_list = []
        if o["bad_respose"] == True:
            flag_list.append("bad_response")
        if "error_list" in o:
            flag_list.append("error_response")
        if flag_list == []:
            if "validation" not in o:
                flag_list.append("schema_validation_failed")
            elif o["validation"]["status"] == "failed":
                flag_list.append("schema_validation_failed")

        flags = ""
        if flag_list != []:
            flags = "failed:" + ";".join(flag_list)
        else:
            flags = "success" 
        row = [main_id, flags]
        with open(summary_file, "a") as FW:
            FW.write("%s\n" % (",".join(row)))
        if flags != "success":
            out_file = log_dir + "%s_failure_log_%s_detail.%s.json" % (user_name,record_type, main_id)
            with open(out_file, "w") as FL:
                FL.write("%s\n" % (json.dumps(o, indent=4)))
    FW.close()

    return


def run_from_queries(api_grp, config_obj, server): 

    last_id_api_url = config_obj["base_url"][server] + "/misc/lastid"
        
    user_name = os.getlogin()
    log_dir = config_obj["data_path"] + "/logs/"
    file_list = glob.glob("queries/*.json")
    if api_grp != "all":
        file_list = glob.glob("queries/%s.json" % (api_grp))

    in_file = "queries/qlist/supersearch_querylist.json"
    supersearch_qlist = json.loads(open(in_file, "r").read())
   
    file_list = sorted(file_list)
    if "queries/globalsearch.json" in file_list:
        file_list.pop(file_list.index("queries/globalsearch.json"))

    out_obj_list = []
    last_list_id = ""
    try:
        summary_file = log_dir + "%s_test_summary_%s_mode_1.csv" % (user_name,api_grp)        
        FW = open(summary_file, "w")
       
        for in_file in file_list:
            if is_valid_json(open(in_file, "r").read()) == False:
                res_obj = {"infile":in_file, "error_code": "invalid-query-json"}
                print (json.dumps(res_obj, indent=4))
                continue
            t_obj_dict = json.loads(open(in_file, "r").read())
            for api_name in t_obj_dict:
                cmd = "rm -f " + log_dir + "failure_log_%s*" % (api_name)
                x = subprocess.getoutput(cmd)
                t_obj = t_obj_dict[api_name]
                t_obj["url"] += "/" if t_obj["url"][-1] != "/" else ""
                api_url = config_obj["base_url"][server] + t_obj["url"]
                req_obj_list = []
                if "querylist" in t_obj:
                    if api_name.find("supersearch") != -1:
                        t_obj["querylist"] = supersearch_qlist
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
                    if "semantic" in t_obj:
                        o["semantic"] = True
                        o.pop("query")
                        api_url += t_obj["query"] + "/"
                        req_obj = {}
                   
                    id_dict_one = get_id_dict_one(last_id_api_url)
                    id_dict_two = get_id_dict_two()
                    grp = api_name.split("_")[0]
                    
                    if grp in id_dict_one:
                        for p in id_dict_one[grp]:
                            if p in req_obj:
                                req_obj[p] = id_dict_one[grp][p]
                    
                    for grp in id_dict_two:
                        for download_type in id_dict_two[grp]:
                            if "type" in req_obj:
                                if download_type == req_obj["type"]:
                                    req_obj["id"] = id_dict_two[grp][download_type]


                    
                    res = requests.post(api_url, json=req_obj, verify=False)
                    #res = requests.get(api_url, json=req_obj, verify=False)
                    #if api_name in ["protein_detail"]:
                    #    continue

                    o["url"] = api_url
                    o["status_code"] = res.status_code
                    if api_name == "glycan_image" or res.headers["Content-Type"] == "image/png":
                        o["validation"] = {"status":"passed"}
                    elif res.headers["Content-Type"] == "application/json":
                        if is_valid_json(res.content) == False:
                            o["bad_respose"] = True
                        else:
                            res_obj = json.loads(res.content)
                            if "error_list" in res_obj:
                                o["error_list"] = res_obj["error_list"]
                            else:
                                if "schemafile" in t_obj:
                                    o["validation"] = validate_response(res_obj,t_obj["schemafile"])
                                else:
                                    o["validation"] = {"status":"noschema"}
                                if "list_id" in res_obj:
                                    last_list_id = res_obj["list_id"]
                    elif "schemafile" not in t_obj:
                        o["validation"] = {"status":"noschema"}

                    flag_list = []
                    if o["bad_respose"] == True:
                        flag_list.append("bad_response")
                    if "error_list" in o:
                        flag_list.append("error_response")
                    if flag_list == []:
                        if "validation" not in o:
                            flag_list.append("schema_validation_failed")
                        elif o["validation"]["status"] == "failed":
                            flag_list.append("schema_validation_failed")
                    flags = ""
                    if flag_list != []:
                        flags = "failed:" + ";".join(flag_list)
                    else:
                        flags = "success"
                    row = [o["name"], "query-"+str(idx), flags]
                    FW.write("%s\n" % (",".join(row)))
                    if flags != "success":
                        out_file = log_dir + "%s_failure_log_%s.%s.json" % (user_name, o["name"], idx)
                        with open(out_file, "w") as FL:
                            FL.write("%s\n" % (json.dumps(o, indent=4)))
                    flg_file = "logs/failure_log_%s.%s.json" % (o["name"], idx)
                    status = "success" if flags == "success" else "failed [see %s]"% (flg_file)


        FW.close()
    except Exception as e:
        print (traceback.format_exc())

    return







