import sys,os
import json
import string
import csv
import traceback
from optparse import OptionParser
from bson import json_util, ObjectId
import supersearch_apilib as apilib
import errorlib
import util


def main():

    usage = "\n%prog  [options]"
    parser = OptionParser(usage,version="%prog version___")
    parser.add_option("-s","--server",action="store",dest="server",help="dev/tst/beta/prd")
    (options,args) = parser.parse_args()
    for key in ([options.server]):
        if not (key):
            parser.print_help()
            sys.exit(0)
                                         
    server = options.server


    global config_obj
    global path_obj
    config_obj = json.loads(open("./conf/config.json", "r").read())
    config_obj["server"] = server
    path_obj  =  config_obj[config_obj["server"]]["pathinfo"]
    db_obj = config_obj[config_obj["server"]]["dbinfo"]

    supersearch_config_obj = json.loads(open("./conf/supersearch.json", "r").read())
    config_obj["ignored_path_list"] = supersearch_config_obj["ignored_path_list"]
    config_obj["path_map"] = supersearch_config_obj["path_map"]
    config_obj["ignored_edges"] = supersearch_config_obj["ignored_edges"]


    res_obj = {}
    #query_obj = [{"query":{"aggregator":"$and","unaggregated_list":[],"aggregated_list":[]}}]
    supersearch_init = {}
    query_obj = {"concept_query_list":[]}
    for record_type in config_obj["record_type_info"]:
        query_obj["concept_query_list"].append({"concept":record_type, "query":{}})

    res_obj = apilib.supersearch_search(query_obj, config_obj, False, True)
    supersearch_init = res_obj["results_summary"]

    print json.dumps(supersearch_init, indent=4)

    dbh, error_obj = util.connect_to_mongodb(db_obj) #connect to mongodb
    if error_obj != {}:
        return error_obj
    q_obj = {}
    update_obj = {"supersearch_init":supersearch_init}
    res = dbh["c_searchinit"].update_one(q_obj, {'$set':update_obj}, upsert=True)



if __name__ == '__main__':
    main()





