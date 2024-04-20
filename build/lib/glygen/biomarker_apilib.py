import os
import string
import random
import hashlib
import json
import datetime,time
import pytz
from collections import OrderedDict
from bson import json_util, ObjectId


from glygen.db import get_mongodb
from glygen.util import get_errors_in_query, sort_objects, order_obj, clean_obj, get_paginated_sections, cache_record_list





def biomarker_detail(query_obj, config_obj):

    dbh, error_obj = get_mongodb()
    if error_obj != {}:
        return error_obj


    #Collect errors 
    error_list = get_errors_in_query("biomarker_detail", query_obj, config_obj)
    if error_list != []:
        return {"error_list":error_list}
    collection = "c_biomarker"

    mongo_query = {"biomarker_canonical_id":{"$eq":query_obj["biomarker_canonical_id"]}}
    obj = dbh[collection].find_one(mongo_query)
    #check for post-access error, error_list should be empty upto this line
    post_error_list = []
    if obj == None:
        post_error_list.append({"error_code":"non-existent-record"})
        return {"error_list":post_error_list}


    
    if "paginated_tables" in query_obj:
        table_id_list = []
        for o in query_obj["paginated_tables"]:
            if o["table_id"] not in table_id_list:
                table_id_list.append(o["table_id"])
        sec_tables = get_paginated_sections(obj, query_obj, table_id_list)
        if "error_list" in sec_tables:
            return sec_tables
        for sec in sec_tables:
            obj[sec] = sec_tables[sec]


    clean_obj(obj, config_obj["removelist"]["c_biomarker"], "c_biomarker")
    obj["crossref"] = []

    return obj




def biomarker_search(query_obj, config_obj):

    dbh, error_obj = get_mongodb()
    if error_obj != {}:
        return error_obj

    #Collect errors 
    error_list = get_errors_in_query("biomarker_search", query_obj,config_obj)
    if error_list != []:
        return {"error_list":error_list}

    mongo_query = get_mongo_query(query_obj)
    #return mongo_query


    collection = "c_biomarker"
    record_list = []
    record_type = "biomarker"
    prj_obj = {"biomarker_canonical_id":1}
    for obj in dbh[collection].find(mongo_query,prj_obj):
        record_list.append(obj["biomarker_canonical_id"])

    ts_format = "%Y-%m-%d %H:%M:%S %Z%z"
    ts = datetime.datetime.now(pytz.timezone('US/Eastern')).strftime(ts_format)
    cache_coll = "c_cache"
    list_id = ""
    if len(record_list) != 0:
        hash_str = record_type + "_" + json.dumps(query_obj)
        hash_obj = hashlib.md5(hash_str.encode('utf-8'))
        list_id = hash_obj.hexdigest()
        cache_info = {
            "query":query_obj,
            "ts":ts,
            "record_type":record_type,
            "search_type":"search"
        }
        cache_record_list(dbh,list_id,record_list,cache_info,cache_coll,config_obj)
    res_obj = {"list_id":list_id}

    return res_obj




def get_mongo_query(query_obj):

                        
    cond_objs = []
    if "biomarker_canonical_id" in query_obj:
        q_id = query_obj["biomarker_canonical_id"]
        cond_objs.append({"biomarker_canonical_id":{'$regex': q_id, '$options': 'i'}})


    operation = query_obj["operation"].lower() if "operation" in query_obj else "and"
    mongo_query = {} if cond_objs == [] else { "$"+operation+"": cond_objs }
       
    return mongo_query








