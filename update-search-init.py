import os,sys
import string
from optparse import OptionParser
import glob
import json
from bson import json_util
import pymongo
from pymongo import MongoClient
import datetime

from lib_update import search
from optparse import OptionParser
from copied_util import get_hash_id, make_list_objects_indirect, cache_list_objects



def update_list_cache(dbh, cache_id, config_obj):

    #cache_id = "e5e9e8999a3451a947eb2f05508b4a29"
    req_obj = {
        "id":cache_id,
        "offset":1,"sort":"hit_score","limit":20,"order":"desc",
        "filters":[],
        "columns":["uniprot_canonical_ac","protein_name","organism",
            "hit_score","start_pos","end_pos","gene_name"
        ]
    }
    
    api_name = "supersearch_list"
    cache_id = req_obj["id"]
    listcache_id = get_hash_id(api_name, "", req_obj)
    
    print ("rerieving list objects ...")
    res_obj = make_list_objects_indirect(dbh, req_obj, config_obj, False)
    print ("done retrieving total of %s results " % (len(res_obj["results"])))
    #res_obj = json.load(open("tmp/JUNK.2"))

    if "error_list" not in res_obj:
        print ("caching list objects ...")
        res = cache_list_objects(dbh, cache_id, listcache_id, res_obj, config_obj)
        print ("done")

    return











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

    config_obj = json.loads(open("./conf/config.json", "r").read())
    mongo_port = "27017"
    host = "mongodb://127.0.0.1:%s" % (mongo_port)
    db_name = "glydb_beta" if server == "beta" else "glydb"
    db_obj = config_obj["dbinfo"][db_name]
    glydb_name, db_user, db_pass =  db_obj["db"], db_obj["user"], db_obj["password"]
    host_ip = config_obj["host_ip"][server]

    config_obj = json.load(open("glygen/conf/config.json"))
    supersearch_config_obj = json.load(open("glygen/conf/supersearch.json"))
    config_obj["ignored_path_list"] = supersearch_config_obj["ignored_path_list"]
    config_obj["path_map"] = supersearch_config_obj["path_map"]
    config_obj["ignored_edges"] = json.load(open("glygen/conf/ignored_edges.json"))
    config_obj["node_order"] = json.load(open("glygen/conf/node_order.json"))
    config_obj["db_info"] = {
        "user":db_user, "password":db_pass, "host_ip":host_ip, "db_name":db_name
    }
 
    req_obj = json.loads(open("conf/init_query.json", "r").read())
    empty_search_flag = True if "empty_search_flag" in req_obj else False
    print ("performing global search with empty query ... ")
    res_obj = search(req_obj, config_obj, False, empty_search_flag)
    #print (json.dumps(res_obj, indent=4))
    #res_obj = json.load(open("tmp/JUNK.1"))
    #get cache_id for site
    cache_id = res_obj["results_summary"]["site"]["list_id"] 
    #print (cache_id)
    print ("done")

    try:
        client = pymongo.MongoClient(host,
            username=db_user,
            password=db_pass,
            authSource=glydb_name,
            authMechanism='SCRAM-SHA-1',
            serverSelectionTimeoutMS=10000
        )
        client.server_info()
        dbh = client[glydb_name]
        
        update_list_cache(dbh, cache_id, config_obj)
        q_obj = {}
        update_obj = {"supersearch_init":res_obj["results_summary"]}
        print ("updating c_searchinit ...")
        res = dbh["c_searchinit"].update_one(q_obj, {'$set':update_obj}, upsert=True)
        print ("done")
    except pymongo.errors.ServerSelectionTimeoutError as err:
        print (err)
    except pymongo.errors.OperationFailure as err:
        print (err)



    return


if __name__ == '__main__':
    main()
