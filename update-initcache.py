import os,sys
import string
import pytz
import datetime
from optparse import OptionParser
import glob
import json
import hashlib
import pymongo
from pymongo import MongoClient
from itertools import combinations

from lib_update import supersearch_search, cache_hitlist, get_mongodb
from optparse import OptionParser
from copied_util import get_hash_id, make_list_objects_indirect, cache_list_objects, get_query_filter_code, get_filter_conf, get_list_objects, get_grp_id_list

from cacheutil import cache_exists, delete_cache, get_c_initcache_queries,get_supersearch_init_query,get_supersearch_log_lines, get_pulldown_dict





def update_c_initcache(dbh, cache_name, list_id, record_type, query_info, config_obj):

    query_obj, main_field = query_info["query"], query_info["mainfield"]
    mongo_query = query_info["mongoquery"]

    search_type = "%s_search" % (record_type)
    coll = "c_" + record_type
    cache_coll = "c_initcache"
    record_list = []
    prj_obj = {main_field:1}
    for obj in dbh[coll].find(mongo_query,prj_obj):
        record_list.append(obj[main_field])
    #print (mongo_query)
    #print (len(record_list))
 
    res_obj = {}
    if cache_name.find("_all") != -1 or len(record_list) > config_obj["min_list_size_to_cache"]:
        #delete any cache by cache_name
        res = dbh["c_initcache"].delete_many({"cache_info.cache_name":cache_name})

        ts_format = "%Y-%m-%d %H:%M:%S %Z%z"
        ts = datetime.datetime.now(pytz.timezone('US/Eastern')).strftime(ts_format)
        cache_info = {
            "cache_name":cache_name,
            "query":query_obj,
            "ts":ts,
            "record_type":record_type,
            "search_type":search_type
        }
        cache_hitlist(dbh,list_id,record_list,cache_info,cache_coll,config_obj)
        res_obj = {"list_id":list_id, "recordcount":len(record_list)}
    else:
        res_obj = {"list_id":list_id, "recordcount":len(record_list), "flag":"not_large"}
    return res_obj




def main():

    usage = "\n%prog  [options]"
    parser = OptionParser(usage,version="%prog version___")
    parser.add_option("-s","--server",action="store",dest="server",help="dev/tst/beta/prd")
    parser.add_option("-n","--cachename",action="store",dest="cachename",help="")
    
    
    (options,args) = parser.parse_args()
    for key in ([options.server, options.cachename]):
        if not (key):
            parser.print_help()
            sys.exit(0)
                                         
    server = options.server
    cache_name = options.cachename
    record_type = cache_name.split("_")[0]
    coll = "c_initcache"

    global seen_child



    db_name = "glydb_beta" if server == "beta" else "glydb"
    config_obj = json.loads(open("./conf/config.json", "r").read())
    db_obj = config_obj["dbinfo"][db_name]
    glydb_name, db_user, db_pass =  db_obj["db"], db_obj["user"], db_obj["password"]
    host_ip = config_obj["host_ip"][server]
    config_obj = json.load(open("glygen/conf/config.json"))
    config_obj["db_info"] = {"user":db_user, "password":db_pass, "host_ip":host_ip, "db_name":db_name}
           
    
    dbh, error_obj = get_mongodb(config_obj["db_info"])
    if error_obj != {}:
        print (error_obj)
        exit()

    pulldown_dict = get_pulldown_dict(dbh, config_obj)
        
    if record_type == "supersearch":
        supersearch_config_obj = json.load(open("glygen/conf/supersearch.json"))
        config_obj["ignored_path_list"] = supersearch_config_obj["ignored_path_list"]
        config_obj["path_map"] = supersearch_config_obj["path_map"]
        config_obj["ignored_edges"] = json.load(open("glygen/conf/ignored_edges.json"))
        config_obj["node_order"] = json.load(open("glygen/conf/node_order.json"))
        query_doc = get_supersearch_init_query(dbh, config_obj, pulldown_dict)
        qry_dict = query_doc[record_type]
        if cache_name in qry_dict:
            qry_obj = qry_dict[cache_name]
            empty_search_flag = True if cache_name == "supersearch_all" else False
            res_obj = supersearch_search(qry_obj["query"], config_obj,False,empty_search_flag, cache_name)
            log_lines = get_supersearch_log_lines(res_obj, cache_name)
            log_file = "logs/c_initcache.%s.log" % (cache_name)
            with open(log_file, "w") as FL:
                for line in log_lines:
                    FL.write("%s\n" % (line))
    elif record_type in ["protein", "glycan", "biomarker", "disease"]:
        query_doc = get_c_initcache_queries(dbh, config_obj, pulldown_dict)
        qry_dict = query_doc[record_type]
        qry_obj = query_doc[record_type][cache_name]
        api_name = "%s_search" % (record_type)
        list_id = get_hash_id(api_name, record_type, qry_obj["query"])
        print (list_id, api_name, record_type, qry_obj["query"])
        if cache_exists(dbh, list_id,  "c_initcache"):
            delete_cache(dbh, list_id, "c_initcache")
        res_obj = update_c_initcache(dbh, cache_name, list_id, record_type, qry_obj, config_obj)
        if "flag" not in res_obj:
            log_file = "logs/c_initcache.%s.log" % (cache_name)
            with open(log_file, "w") as FL:
                FL.write("%s,%s,%s\n" % (list_id, res_obj["recordcount"],cache_name))


    return


if __name__ == '__main__':
    main()
