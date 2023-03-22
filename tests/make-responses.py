import sys,os
import json
import string
import traceback
from optparse import OptionParser
from bson import json_util, ObjectId
import requests
import glob
import urllib3

import jsonref
from jsonschema import validate, Draft4Validator

urllib3.disable_warnings()


def is_valid_json(myjson):
    try:
        json_object = json.loads(myjson)
    except ValueError as e:
        return False
    return True




def main():
    

    file_list = glob.glob("queries/*.json")
    file_list = ['queries/protein.json']

    in_file = "queries/qlist/supersearch_querylist.json"
    supersearch_qlist = json.loads(open(in_file, "r").read())
    
    
    out_obj_list = []
    #base_url = "https://api.dev.glygen.org"
    base_url = "http://localhost:8082/"




    last_list_id = ""
    try:
        for in_file in file_list:
            if is_valid_json(open(in_file, "r").read()) == False:
                res_obj = {"infile":in_file, "error_code": "invalid-query-json"}
                print (json.dumps(res_obj, indent=4))
                continue

            test_obj_dict = json.loads(open(in_file, "r").read())
            for api_name in test_obj_dict:
                test_obj = test_obj_dict[api_name]
                test_obj["url"] += "/" if test_obj["url"][-1] != "/" else ""
                api_url = base_url + test_obj["url"]
                req_obj_list = []
                if "querylist" in test_obj:
                    if api_name.find("supersearch") != -1:
                        test_obj["querylist"] = supersearch_qlist
                    for o in test_obj["querylist"]:
                        req_obj_list.append(o["query"])
                elif "query" in test_obj:
                    if api_name.find("_list") != -1 and "id" in test_obj["query"]:
                        test_obj["query"]["id"] = last_list_id
                    req_obj_list.append(test_obj["query"])
                idx = 0
                for req_obj in req_obj_list:
                    idx += 1
                    if "semantic" in test_obj:
                        api_url += test_obj["query"] + "/"
                        req_obj = {}
                    res = requests.post(api_url, json=req_obj, verify=False)
                    if is_valid_json(res.content) == True:
                        res_obj = json.loads(res.content)
                        if "error_list" in res_obj:
                            err = json.dumps(res_obj["error_list"])
                            print ("ERROR: %s, [%s] " %(api_name, err))
                        else:
                            if "list_id" in res_obj:
                                last_list_id = res_obj["list_id"]
                            out_file = "responses/%s.json" % (api_name)
                            with open(out_file, "w") as FW:
                                FW.write("%s\n" % (json.dumps(res_obj, indent=4)))
                            print ("created %s" % (out_file))

    except Exception as e:
        print (traceback.format_exc())


if __name__ == '__main__':
    main()





