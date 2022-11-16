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
    res["status"] = "passed" if res["error_list"] == [] else "failed"

    return res






def main():
    
    usage = "\n%prog  [options]"
    parser = OptionParser(usage,version="%prog version___")
    parser.add_option("-s","--server",action="store",dest="server",help="dev/tst/beta/prd")
    parser.add_option("-c","--apiclass",action="store",dest="apiclass",help="[all, protein, glycan ...]")
    
    (options,args) = parser.parse_args()
    for key in ([options.server, options.apiclass]):
        if not (key):
            parser.print_help()
            sys.exit(0)

    log_dir = "/data/shared/glygen/logs/"
    if options.server == "dev":
        log_dir = "/Volumes/disk2/data/shared/glygen/logs/"

    api_class = options.apiclass
    file_list = glob.glob("queries/*.json")
    if api_class != "all":
        file_list = ["queries/%s.json" % (api_class)]

    in_file = "queries/qlist/supersearch_querylist.json"
    supersearch_qlist = json.loads(open(in_file, "r").read())

    
    
    out_obj_list = []
    #base_url = "https://api.dev.glygen.org"
    base_url = "http://localhost:5000"
    
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
                    o = {"name":api_name, "class":api_class, "query":req_obj, 
                            "valid_respose":True, "semantic":False}
                    if "semantic" in test_obj:
                        o["semantic"] = True
                        o.pop("query")
                        api_url += test_obj["query"] + "/"
                        req_obj = {}
                    res = requests.post(api_url, json=req_obj, verify=False)
                    o["url"] = api_url
                    o["status_code"] = res.status_code
                    if is_valid_json(res.content) == False:
                        o["valid_respose"] = False
                    else:
                        res_obj = json.loads(res.content)
                        if "error_list" in res_obj:
                            o["error_list"] = res_obj["error_list"]
                        else:
                            if "schemafile" in test_obj:
                                v_obj = validate_response(res_obj, test_obj["schemafile"])
                                print (v_obj)
                            out_file = "responses/%s.json" % (o["name"])
                            with open(out_file, "w") as FW:
                                FW.write("%s\n" % (json.dumps(res_obj, indent=4)))
                            if type(res_obj) is dict:
                                o["p_count"] = len(list(res_obj.keys()))
                                o["response_class"] = "dict"
                            elif type(res_obj) is list:
                                o["p_count"] = len(res_obj)
                                o["response_class"] = "list"
                            #o["p_count"] = len(list(res_obj.keys()))
                            if "list_id" in res_obj:
                                last_list_id = res_obj["list_id"]
                    flag_list = [str(o["valid_respose"]), str("error_list" not in o)]
                    #if False in flag_list:
                    out_file = log_dir + "api_test_%s.%s.json" % (o["name"], idx)
                    with open(out_file, "w") as FW:
                        FW.write("%s\n" % (json.dumps(o, indent=4)))
    except Exception as e:
        print (traceback.format_exc())


if __name__ == '__main__':
    main()





