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
        res["error_list"].append(error.message)
        #res["error_list"].append(error)

    res["status"] = "passed" if res["error_list"] == [] else "failed"

    return res



def get_id_dict():

    id_dict = {}
    api_url = config_obj["base_url"] + "/misc/lastid"
    res = requests.post(api_url, json={}, verify=False)
    res_obj = json.loads(res.content)
    for coll in res_obj:
        p = coll[2:]
        id_dict[p] = res_obj[coll]
        if "_id" in id_dict[p]:
            id_dict[p]["id"] = id_dict[p]["_id"]
    return id_dict



def run_exhaustive(api_grp):

    api_url = config_obj["base_url"] + "/misc/info"
    res = requests.post(api_url, json={}, verify=False)
    info_obj =  json.loads(res.content)
    data_version = info_obj["initobj"]["dataversion"]

    jsondb_dir = config_obj["data_path"] + "releases/data/v-%s/jsondb/" % (data_version)
    log_dir = config_obj["data_path"]  + "/logs/"

    api_url = config_obj["base_url"] + "/misc/info"
    res = requests.post(api_url, json={}, verify=False)
    info_obj =  json.loads(res.content)
    data_version = info_obj["initobj"]["dataversion"]


    cmd = "rm -f " + log_dir + "failure_log_%s_detail.*" % (api_grp)
    x = subprocess.getoutput(cmd)

                                    

    file_list = glob.glob(jsondb_dir + "%sdb/*.json" % (api_grp))
    file_list = file_list[0:10]
    try:
        summary_file = log_dir + "test_summary_%s_mode_2.csv" % (api_grp)
        FW = open(summary_file, "w")
                       

        for in_file in file_list:
            main_id = in_file.split("/")[-1].replace(".json", "")
            api_url = config_obj["base_url"] + "/%s/detail/%s/" % (api_grp, main_id)
            req_obj = {}
            if api_grp in ["motif"]:
                api_url = config_obj["base_url"] + "/%s/detail/" % (api_grp)
                req_obj = {"motif_ac":main_id}

            o = {"bad_respose":False, "url":api_url}
            res = requests.post(api_url, json=req_obj, verify=False)
            o["status_code"] = res.status_code
            if is_valid_json(res.content) == False:
                o["bad_respose"] = True
            else:
                res_obj = json.loads(res.content)
                if "error_list" in res_obj:
                    o["error_list"] = res_obj["error_list"]
                else:
                    schema_file = "../specs/%s/detail/response.schema.json" % (api_grp)
                    o["validation"] =validate_response(res_obj,schema_file)
            
            flag_list = []
            if o["bad_respose"] == True:
                flag_list.append("bad_response")
            if "error_list" in o:
                flag_list.append("error_response")
            if flag_list == [] and o["validation"]["status"] == "failed":
                flag_list.append("invalid_response")
            flags = "success" if flag_list == [] else "failed:" + ";".join(flag_list)
            row = [api_grp, main_id, flags]
            FW.write("%s\n" % (",".join(row)))

            if flags != "success":
                out_file = log_dir + "failure_log_%s_detail.%s.json" % (api_grp, main_id)
                with open(out_file, "w") as FL:
                    FL.write("%s\n" % (json.dumps(o, indent=4)))
        FW.close()
        print ("\nSummary output file: %s\n" %(summary_file))
    except Exception as e:
        print (traceback.format_exc())


    return


def run_from_queries(api_grp):
    
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
        summary_file = log_dir + "test_summary_%s_mode_1.csv" % (api_grp)        
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
                api_url = config_obj["base_url"] + t_obj["url"]
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
                   
                    id_dict = get_id_dict()
                    grp = api_name.split("_")[0]
                    if grp in id_dict:
                        for p in id_dict[grp]:
                            if p in req_obj:
                                req_obj[p] = id_dict[grp][p]
                    res = requests.post(api_url, json=req_obj, verify=False)
                    o["url"] = api_url
                    o["status_code"] = res.status_code
                    if res.headers["Content-Type"] == "image/png":
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
                                    o["validation"] =validate_response(res_obj,t_obj["schemafile"])
                                if "list_id" in res_obj:
                                    last_list_id = res_obj["list_id"]
                    flag_list = []
                    if o["bad_respose"] == True:
                        flag_list.append("bad_response")
                    if "error_list" in o:
                        flag_list.append("error_response")
                    if flag_list == [] and o["validation"]["status"] == "failed":
                        flag_list.append("invalid_response")
                    flags = "success" if flag_list == [] else "failed:" + ";".join(flag_list)
                    row = [o["name"], "query-"+str(idx), flags]
                    FW.write("%s\n" % (",".join(row)))
                    if flags != "success":
                        out_file = log_dir + "failure_log_%s.%s.json" % (o["name"], idx)
                        with open(out_file, "w") as FL:
                            FL.write("%s\n" % (json.dumps(o, indent=4)))
                    flg_file = "logs/failure_log_%s.%s.json" % (o["name"], idx)
                    status = "success" if flags == "success" else "failed [see %s]"% (flg_file)

        print ("\nSummary output file: %s\n" %(summary_file))

        FW.close()
    except Exception as e:
        print (traceback.format_exc())

    return


def main():
   
    usage = "\n%prog  [options]"
    parser = OptionParser(usage,version="%prog version___")
    parser.add_option("-m","--mode",action="store",dest="mode",help="1 (using example queries), 2 (exhaustive detail API calls)")
    parser.add_option("-g","--group",action="store",dest="group",help="all/protein/glycan/...")
        

    (options,args) = parser.parse_args()
    for key in ([options.group, options.mode]):
        if not (key):
            parser.print_help()
            sys.exit(0)

    api_grp = options.group
    mode = int(options.mode)

    global config_obj

    config_obj = json.loads(open("./conf/config.json", "r").read())
        

    if mode == 2:
        run_exhaustive(api_grp)
    else:
        run_from_queries(api_grp)

    return






if __name__ == '__main__':
    main()





