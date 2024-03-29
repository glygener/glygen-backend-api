import os
import string
import random
import hashlib
import json
import datetime,time
import pytz
from collections import OrderedDict
from bson import json_util, ObjectId
import collections


from glygen.db import get_mongodb
from glygen.util import cache_record_list, get_errors_in_query


def search_init(config_obj):
    
    dbh, error_obj = get_mongodb()
    if error_obj != {}:
        return error_obj

    collection = "c_searchinit"
    doc =  dbh[collection].find_one({})

    doc["idmapping"]["glycan"]["organism"] = doc["glycan"]["organism"]
    doc["idmapping"]["protein"]["organism"] = doc["protein"]["organism"]    


    res_obj = doc["idmapping"]
    for k in res_obj:
        if "namespace" in res_obj[k]:
            tmp_dict = {}
            for obj in res_obj[k]["namespace"]:
                tmp_dict[obj["source"]] = {"target_list":obj["targetlist"], "example_id_list":obj["example_id_list"]}
            res_obj[k]["namespace"] = tmp_dict
    
    return res_obj



def search(query_obj, config_obj):
    
    dbh, error_obj = get_mongodb()
    if error_obj != {}:
        return error_obj

    q_list = []
    for q in query_obj["input_idlist"]:
        q_list.append(q)


    mongo_query = {"crossref.id":{"$in": q_list}}
    record_id_field = config_obj["record_type_info"][query_obj["recordtype"]]["field"]
    record_id_label = config_obj["record_type_info"][query_obj["recordtype"]]["label"]


    
    coll = "c_" + query_obj["recordtype"]
    prj_obj = {"crossref":1, record_id_field:1}



    mapping_dict = {}
    for doc in dbh[coll].find(mongo_query,prj_obj):
        in_list, out_list = [], []
        for obj in doc["crossref"]:
            if obj["id"].strip() == "":
                continue
            if obj["database"] == query_obj["input_namespace"] and obj["id"] in q_list:
                in_list.append(obj["id"])
            if obj["database"] == query_obj["output_namespace"]:
                out_list.append(obj["id"])
        for in_id in in_list:
            if in_id not in mapping_dict:
                mapping_dict[in_id] = []

            for out_id in out_list:
                if out_id not in mapping_dict[in_id]:
                    i_id = int(in_id) if in_id.isdigit() == True else in_id
                    o_id = int(out_id) if out_id.isdigit() == True else out_id
                    o = {"anchor":doc[record_id_field], "from":i_id, "to":o_id,"category":"mapped"}
                    mapping_dict[in_id].append(o)
   


    all_glytoucan_dict = {}
    #If input_namespace is GlyToucan, check all glytoucan_idlist
    if query_obj["input_namespace"].lower() == "glytoucan":
        for doc in dbh["c_glytoucan"].find({}):
            for ac in doc["aclist"]:
                all_glytoucan_dict[ac] = True

    record_list = []
    for in_id in mapping_dict:
        for o in mapping_dict[in_id]:
            record_list.append(o)

    for in_id in q_list:
        if in_id not in mapping_dict:
            reason = "Invalid ID"
            if in_id in all_glytoucan_dict:
                reason = "Valid GlyTouCan accession but not in GlyGen"
            record_list.append({"input_id":in_id, "reason": reason, "category":"unmapped"})
        elif mapping_dict[in_id] == []:
            reason = "Valid ID, no mapping found"
            record_list.append({"input_id":in_id, "reason": reason, "category":"unmapped"})
    

    mapped_legends = {
        "from":query_obj["input_namespace"],
        "to":query_obj["output_namespace"],
        "anchor":record_id_label
    }
    unmapped_legends = {
        "input_id":"Input ID",
        "reason":"Reason"
    }
    record_type = "idmap"
    ts_format = "%Y-%m-%d %H:%M:%S %Z%z"
    ts = datetime.datetime.now(pytz.timezone('US/Eastern')).strftime(ts_format)
    cache_coll = "c_cache"
    
    cache_info = {
        "query":query_obj,
        "mapped_legends":mapped_legends,
        "unmapped_legends":unmapped_legends, 
        "ts":ts
    }
    list_id = ""
    if len(record_list) != 0:
        hash_str = record_type + "_" + ",".join(query_obj["input_idlist"]).strip()
        hash_obj = hashlib.md5(hash_str.encode('utf-8'))
        list_id = hash_obj.hexdigest()
        cache_record_list(dbh,list_id,record_list,cache_info,cache_coll,config_obj)
    res_obj = {"list_id":list_id}

    return res_obj

