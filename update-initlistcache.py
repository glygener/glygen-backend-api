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
from copied_util import get_hash_id, make_list_objects_indirect, cache_list_objects, get_query_filter_code, get_filter_conf, get_list_objects, get_grp_id_list, get_taxid2name

from cacheutil import cache_exists, delete_cache, get_c_initcache_queries,get_supersearch_log_lines, get_cache_id_dict, get_c_initlistcache_queries, get_column_dict



def update_c_initlistcache(dbh, in_dict):

    query_obj, config_obj = in_dict["query_obj"], in_dict["config_obj"]
    api_name, rt = in_dict["api_name"], in_dict["rt"]
    cache_name, cache_id = in_dict["cache_name"], in_dict["cache_id"]
    
    prefix = api_name
    # this is done because the supersearch diagram uses these prefixes
    if api_name.find("supersearch") != -1 and rt in ["glycan", "protein", "disease"]:
        prefix = "%s_list" % (rt)
    listcache_id = get_hash_id(prefix, "", query_obj)

    res_obj = make_list_objects_indirect(dbh, query_obj, config_obj, False)
    if cache_exists(dbh, listcache_id, "c_initlistcache"):
        delete_cache(dbh, listcache_id, "c_initlistcache")
   
    if "pagination" not in res_obj:
        print (json.dumps(res_obj, indent=4))
        exit()
 
    list_size = res_obj["pagination"]["total_length"]
    #if list_size > config_obj["min_list_size_to_cache"]:
    res = cache_list_objects(dbh, api_name, cache_id, listcache_id, res_obj, config_obj)
    if "error_list" in res:
        print (res)
        exit()

    grp_id, opt_id = "none", "none"
    if len(query_obj["filters"])  > 0:
        grp_id = query_obj["filters"][0]["id"]
        opt_id = query_obj["filters"][0]["selected"][0]
    log_file = "logs/c_initlistcache.%s.log" % (cache_name)
    with open(log_file, "a") as FL:
        FL.write("%s,%s,%s,%s,%s,%s,%s\n" % (cache_id, listcache_id, list_size,grp_id, opt_id, cache_name,rt))

    count_dict = {}
    for obj in res_obj["filters"]["available"]:
        grp_id, f_lbl = obj["id"], obj["label"]
        for o in obj["options"]:
            opt_id, n = o["id"], o["count"]
            if grp_id not in count_dict:
                count_dict[grp_id] = {}
            count_dict[grp_id][opt_id] = n

    return count_dict, listcache_id, list_size



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
    coll = "c_initlistcache"

    global seen_child
    global taxid2name


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

    taxid2name = get_taxid2name(dbh, default=False)
    column_dict = get_column_dict()
    
    query_doc = get_c_initlistcache_queries(dbh, config_obj)
    qry_dict = query_doc[record_type]
    api_name = "%s_list" % (record_type)
    log_file = "logs/c_initlistcache.%s.log" % (api_name)
    cache_coll = "c_initcache"
    qry_dict = query_doc[record_type]
    qry_obj = query_doc[record_type][cache_name]

    cache_id_dict = get_cache_id_dict(dbh, cache_name)
    # for this cachename, make list cache only for site objects
    if cache_name.find("supersearch_startaa_") != -1 or cache_name.find("_flag") != -1:
        k_list = list(cache_id_dict.keys()) 
        for k in k_list:
            if cache_id_dict[k] != "site":
                cache_id_dict.pop(k)
    if cache_id_dict == {}:
        print ("no cache_id(s) related to cache_name=%s" % (cache_name))
        exit()
    #print (cache_id_dict)
    #exit()
    
    log_file = "logs/c_initlistcache.%s.log" % (cache_name)
    with open(log_file, "w") as FL:
        FL.write("")
    
    output_dict = {}
    for cache_id in cache_id_dict:
        rt = cache_id_dict[cache_id]
        qry_obj["query"]["id"] = cache_id
        qry_obj["query"]["columns"] = column_dict[rt] if rt != "site" else column_dict["supersearch"]
        cached_obj = dbh[cache_coll].find_one({"list_id":cache_id})
        cache_info = cached_obj["cache_info"]
        in_dict = {
            "query_obj":qry_obj["query"], "api_name":api_name, "cache_name":cache_name,
            "cache_id":cache_id, "rt":rt, "config_obj":config_obj
        }
        count_dict, listcache_id, list_size = update_c_initlistcache(dbh, in_dict)
        output_dict[cache_id] = {"countdict":count_dict, "listcacheid":listcache_id, "listsize":list_size} 

    for cache_id in output_dict:
        count_dict = output_dict[cache_id]["countdict"]
        for grp_id in count_dict:
            for opt_id in count_dict[grp_id]:
                opt_list = [opt_id]
                in_dict["query_obj"]["filters"] = [{"id":grp_id,"operator":"OR","selected":opt_list}]
                tmp_count_dict, listcache_id, list_size = update_c_initlistcache(dbh, in_dict)

    return


if __name__ == '__main__':
    main()
