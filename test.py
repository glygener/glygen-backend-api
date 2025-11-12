import os,sys
import string
import glob
import json
import pymongo
from pymongo import MongoClient
import datetime
import pytz
from lib_update import supersearch_search, cache_hitlist, get_mongodb
from copied_util import get_hash_id, make_list_objects_indirect, cache_list_objects, update_filters, get_filter_conf, get_query_filter_code

###############################
def get_combined_cached_result_list(dbh, cache_id, record_type, f_obj_list):

    ts_format = "%Y-%m-%d %H:%M:%S %Z%z"
    ts_list = []
    ts_list.append("1- "+datetime.datetime.now(pytz.timezone('US/Eastern')).strftime(ts_format))
 
    query_obj = {"id":cache_id,"offset":1,"limit":20,"order":"desc","sort":"hit_score","filters":[]}
    api_name = "%s_list" % (record_type)
    prj_obj = {"results.record_id"}
    record_dict = {}
    seen_listcache_id = {}
    for f_obj in f_obj_list:
        grp_id, operator, opt_id_list = f_obj["id"], f_obj["operator"], f_obj["selected"]
        tmp_dict = {}
        for opt_id in opt_id_list:
            query_obj["filters"] = [{"id":grp_id,"operator":"OR","selected":[opt_id]}]
            listcache_id = get_hash_id(api_name, "", query_obj)
            tmp_dict[opt_id] = []
            for doc in dbh["c_initlistcache"].find({"list_id":listcache_id}, prj_obj):
                r_list = []
                for o in doc["results"]:
                    r_list.append(o["record_id"])
                tmp_dict[opt_id] += r_list
                seen_listcache_id[listcache_id] = True

        record_dict[grp_id] = []
        if operator.lower() == "or":
            for opt_id in opt_id_list:
                record_dict[grp_id] = list(set(record_dict[grp_id] + tmp_dict[opt_id]))
        elif operator.lower() == "and":
            record_dict[grp_id] = tmp_dict[opt_id_list[0]]
            if len(opt_id_list) > 1:
                for opt_id in opt_id_list[1:]:
                    new_list = tmp_dict[opt_id]
                    record_dict[grp_id] = list(set(new_list).intersection(set(record_dict[grp_id])))


    grp_id_list = list(record_dict.keys())
    final_list = record_dict[grp_id_list[0]]
    if len(grp_id_list) > 1:
        for grp_id in grp_id_list[1:]:
            final_list = list(set(final_list).intersection(set(record_dict[grp_id])))
   
    final_dict = {}
    for record_id in final_list:
        final_dict[record_id] = True   
 
    ts_list.append("2- "+datetime.datetime.now(pytz.timezone('US/Eastern')).strftime(ts_format))
    first_doc = {} 
    obj_dict = {} 
    prj_obj = {"glbl":1, "results.record_id":1, "results.filter_code":1}
    for listcache_id in seen_listcache_id:
        if len(obj_dict.keys()) > len(final_list):
            break
        for doc in dbh["c_initlistcache"].find({"list_id":listcache_id}, prj_obj):
            if "glbl" in doc:
                if doc["glbl"] != {} and first_doc == {}:
                    first_doc = doc
            for o in doc["results"]:
                if o["record_id"] in final_dict:
                    obj_dict[o["record_id"]] = o
                    if len(obj_dict.keys()) > len(final_list):
                        break
    ts_list.append("3- "+datetime.datetime.now(pytz.timezone('US/Eastern')).strftime(ts_format))

    api_name = "%s_list" % (record_type)
    query_obj["filters"] = f_obj_list
    final_listcache_id = get_hash_id(api_name, "", query_obj)

    res_obj = {"results":[], "filters":{"applied":[], "available":[]}}
    for k in first_doc["glbl"]:
        res_obj[k] = first_doc["glbl"][k]
    for record_id in obj_dict:
        res_obj["results"].append(obj_dict[record_id])
    total_length = len(res_obj["results"])


    filter_conf = get_filter_conf(dbh)
    query_filters = query_obj["filters"] if "filters" in query_obj else []
    res = get_query_filter_code(dbh,query_filters, record_type, filter_conf)
    query_filter_code, code_dict = res["code"], res["dict"]
    update_res = update_filters(record_type, res_obj["results"], res_obj["filters"], 1, code_dict, filter_conf)
    if "error_list" in update_res:
        return update_res


    if len(res_obj["results"]) == 0:
        return None
    if "cache_info" not in res_obj:
        res_obj["cache_info"] = {}
    res_obj["cache_info"]["cache_id"] = cache_id
    res_obj["cache_info"]["listcache_id"] = final_listcache_id
    res_obj["pagination"] = {
        "offset":query_obj["offset"],
        "limit":query_obj["limit"],
        "total_length":total_length,
        "sort":query_obj["sort"],
        "order":query_obj["order"]
    }

    ts_list.append("4- "+datetime.datetime.now(pytz.timezone('US/Eastern')).strftime(ts_format))
    #print (json.dumps(ts_list, indent=4))

    return res_obj


###############################
def main():


    server = "tst"
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


    #record_type = "glycan"
    #cache_id = "34e9b2754d2f89a5a45e947c2eb5c783"
    record_type = "protein"
    cache_id = "f3da238e7ac37cc5058f73be99cb434d"

    filter_conf = get_filter_conf(dbh)
    grpid2optidlist = {}
    for grp_id in filter_conf[record_type]:
        grpid2optidlist[grp_id] = []
        for opt_id in filter_conf[record_type][grp_id]["order_dict"]:
            grpid2optidlist[grp_id].append(opt_id)

    o_dict = {}
    grp_id_list = list(grpid2optidlist.keys())
    for grp_size in range(1, len(grp_id_list)):
        for grp_id in grp_id_list[0:grp_size]:
            opt_id_list = grpid2optidlist[grp_id]
            for opt_size in range(1, len(opt_id_list)):
                o = {"id":grp_id , "operator": "OR", "selected":opt_id_list[0:opt_size]}
                if grp_size not in o_dict:
                    o_dict[grp_size] = {}
                if opt_size not in o_dict[grp_size]:
                    o_dict[grp_size][opt_size] = []
                o_dict[grp_size][opt_size].append(o)
    for grp_size in o_dict:
        for opt_size in o_dict[grp_size]:
    #for grp_size in [5]:
    #    for opt_size in [5]:
            f_obj_list = o_dict[grp_size][opt_size]
            start_ts = datetime.datetime.now(pytz.timezone('US/Eastern'))
            res_obj  = get_combined_cached_result_list(dbh, cache_id, record_type, f_obj_list)
            end_ts = datetime.datetime.now(pytz.timezone('US/Eastern'))
            diff = end_ts - start_ts
            print (diff, grp_size, opt_size)
 
    #print (json.dumps(f_obj_list, indent=4))
    #print (len(res_obj["results"]))

    return




if __name__ == '__main__':
    main()
