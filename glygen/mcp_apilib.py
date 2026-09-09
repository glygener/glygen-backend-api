import os
import string
import random
import hashlib
import json
import datetime,time
import pytz
from collections import OrderedDict


from glygen.db import get_mongodb
from glygen.util import cache_hitlist, clean_obj, extract_name, get_errors_in_query, get_paginated_sections,get_hash_id



def site_search(query_obj, config_obj):

    dbh, error_obj = get_mongodb()
    if error_obj != {}:
        return error_obj


    error_list = get_errors_in_query("mcp_site_search",query_obj, config_obj)
    if error_list != []:
        return {"error_list":error_list}


    record_type = "site"
    api_name = "site_search"
    list_id = get_hash_id(api_name, record_type, query_obj)

    #Get cached object
    cache_coll = "c_initcache"
    mongo_query = {"list_id":list_id}
    cached_obj = dbh[cache_coll].find_one(mongo_query)
    if cached_obj == None:
        cache_coll = "c_usercache"
        cached_obj = dbh[cache_coll].find_one(mongo_query)


    result_id = "glycosites_experimental." + list_id
    if cached_obj != None:
        if len(cached_obj["results"]) > 0:
            return {
                "tissue_id":cached_obj["cache_info"]["query"]["tissue_id"],
                "tissue_name":cached_obj["cache_info"]["query"]["tissue_name"],
                "tax_id":cached_obj["cache_info"]["query"]["tax_id"],
                "result_id":result_id, 
                "resultcount":cached_obj["total_count"], 
                "source":cache_coll
            }
 
    tmp_dict = {}
    if "tissue_id" in query_obj and "tax_id" in query_obj:
        qry_obj = {
            "expression_tissue.tissue.id" : {'$eq':query_obj["tissue_id"]}, 
            "species.taxid":{"$eq":query_obj["tax_id"]}
        }
        prj_obj = {"uniprot_canonical_ac":1, "expression_tissue":1, "glycosylation":1, "snv":1}
        for doc in dbh["c_protein"].find(qry_obj, prj_obj):
            ac = doc["uniprot_canonical_ac"].split("-")[0]
            flag = False
            for obj in doc["expression_tissue"]:
                if obj["tissue"]["id"] == query_obj["tissue_id"] and obj["present"] in ["HIGH", "MEDIUM"]:
                    query_obj["tissue_name"] = obj["tissue"]["name"]
                    flag = True
                    break
            if flag:
                for obj in doc["glycosylation"]:
                    cat = obj["site_category"] if "site_category" in obj else ""
                    if "start_pos" in obj and cat.find("reported") != -1:
                        if obj["start_pos"] > 1 and obj["start_pos"] == obj["end_pos"]:
                            site = "%s:%s:%s" % (ac, obj["start_pos"], obj["start_aa"])
                            tmp_dict[site] = True

    record_list = list(tmp_dict.keys())
    ts_format = "%Y-%m-%d %H:%M:%S %Z%z"
    
    ts = datetime.datetime.now(pytz.timezone('US/Eastern')).strftime(ts_format)
    list_id = "" if len(record_list) == 0 else list_id
    if len(record_list) != 0:
        cache_info = {
            "query":query_obj,
            "ts":ts,
            "record_type":record_type,
            "search_type":"site_search",
            "cache_name":"mcp_glycosites"
        }
        cache_hitlist(dbh,list_id,record_list,cache_info,cache_coll,config_obj)
    res_obj = {
        "tissue_id":query_obj["tissue_id"] if "tissue_id" in query_obj else "",
        "tissue_name":query_obj["tissue_name"] if "tissue_name" in query_obj else "",
        "tax_id":query_obj["tax_id"] if "tax_id" in query_obj else 0,
        "result_id":result_id, 
        "resultcount":len(record_list), 
        "source":"new"
    }
    
    return res_obj






def variant_search(query_obj, config_obj):

    dbh, error_obj = get_mongodb()
    if error_obj != {}:
        return error_obj


    error_list = get_errors_in_query("mcp_variant_search",query_obj, config_obj)
    if error_list != []:
        return {"error_list":error_list}



    record_type = "site"
    api_name = "variant_search"
    list_id = get_hash_id(api_name, record_type, query_obj)

    #Get cached object
    cache_coll = "c_initcache"
    mongo_query = {"list_id":list_id}
    cached_obj = dbh[cache_coll].find_one(mongo_query)
    if cached_obj == None:
        cache_coll = "c_usercache"
        cached_obj = dbh[cache_coll].find_one(mongo_query)


    result_id = "disease_variants." + list_id
    if cached_obj != None:
        if len(cached_obj["results"]) > 0:
            return {
                "tissue_id":cached_obj["cache_info"]["query"]["tissue_id"],
                "tissue_name":cached_obj["cache_info"]["query"]["tissue_name"],
                "tax_id":cached_obj["cache_info"]["query"]["tax_id"],
                "result_id":result_id, 
                "resultcount":cached_obj["total_count"], 
                "source":cache_coll
            }
 
    tmp_dict = {}
    if "tissue_id" in query_obj and "tax_id" in query_obj:
        qry_obj = {
            "expression_tissue.tissue.id" : {'$eq':query_obj["tissue_id"]}, 
            "species.taxid":{"$eq":query_obj["tax_id"]}
        }
        prj_obj = {"uniprot_canonical_ac":1, "expression_tissue":1, "glycosylation":1, "snv":1}
        for doc in dbh["c_protein"].find(qry_obj, prj_obj):
            ac = doc["uniprot_canonical_ac"].split("-")[0]
            flag = False
            for obj in doc["expression_tissue"]:
                if obj["tissue"]["id"] == query_obj["tissue_id"] and obj["present"] in ["HIGH", "MEDIUM"]:
                    query_obj["tissue_name"] = obj["tissue"]["name"]
                    flag = True
                    break
            if flag:
                for obj in doc["snv"]:
                    disease_flag = "disease_yes" if "disease" in obj["keywords"] else "disease_no"
                    if "start_pos" in obj:
                        if obj["start_pos"] > 1 and obj["start_pos"] == obj["end_pos"]:
                            ref_aa, alt_aa = obj["sequence_org"], obj["sequence_mut"]
                            site = "%s:%s:%s>%s:%s" % (ac, obj["start_pos"], ref_aa, alt_aa,disease_flag)
                            tmp_dict[site] = True

    record_list = list(tmp_dict.keys())
    ts_format = "%Y-%m-%d %H:%M:%S %Z%z"
    
    ts = datetime.datetime.now(pytz.timezone('US/Eastern')).strftime(ts_format)
    list_id = "" if len(record_list) == 0 else list_id
    if len(record_list) != 0:
        cache_info = {
            "query":query_obj,
            "ts":ts,
            "record_type":record_type,
            "search_type":"site_search",
            "cache_name":"mcp_variants"
        }
        cache_hitlist(dbh,list_id,record_list,cache_info,cache_coll,config_obj)
    res_obj = {
        "tissue_id":query_obj["tissue_id"],
        "tissue_name":query_obj["tissue_name"] if "tissue_name" in query_obj else "unknown",
        "tax_id":query_obj["tax_id"],
        "result_id":result_id, 
        "resultcount":len(record_list), 
        "source":"new"
    }
    
    return res_obj



def map_variants(query_obj, config_obj):

    dbh, error_obj = get_mongodb()
    if error_obj != {}:
        return error_obj

    error_list = get_errors_in_query("mcp_map_variants",query_obj, config_obj)
    if error_list != []:
        return {"error_list":error_list}

    record_type = "mapped_variants"
    api_name = "map_variants"
    list_id = get_hash_id(api_name, record_type, query_obj)

    #Get cached object
    cache_coll = "c_initcache"
    mongo_query = {"list_id":list_id}
    cached_obj = dbh[cache_coll].find_one(mongo_query)
    if cached_obj == None:
        cache_coll = "c_usercache"
        cached_obj = dbh[cache_coll].find_one(mongo_query)

    result_id = "mapped_variants." + list_id
    if cached_obj != None:
        if len(cached_obj["results"]) > 0:
            return {
                "site_result_id":query_obj["site_result_id"],
                "variant_result_id":query_obj["variant_result_id"],
                "result_id":result_id,
                "resultcount":cached_obj["total_count"],
                "source":cache_coll
            }
   
    site_list_id = query_obj["site_result_id"].split(".")[1]
    variant_list_id = query_obj["variant_result_id"].split(".")[1] 
    #Get cached object
    cache_coll = "c_usercache"
    site_records, variant_records = [], []
    for doc in dbh[cache_coll].find({"list_id":site_list_id}):
        site_records += doc["results"]
    for doc in dbh[cache_coll].find({"list_id":variant_list_id}):
        variant_records += doc["results"]
    
    site_dict = {}
    for val in site_records:
        ac,pos,site = val.split(":")
        if ac not in site_dict:
            site_dict[ac] = {}
        pos = int(pos)
        if pos not in site_dict[ac]:
            site_dict[ac][pos] = {}
        site_dict[ac][pos][site] = True 

    distance_cutoff = 3

    record_list = []
    variant_dict = {}
    for val in variant_records:
        ac,v_pos,mut,disease_flag = val.split(":")
        v_pos = int(v_pos)
        site_list = []
        if ac in site_dict:
            for s_pos in site_dict[ac]:
                if abs(s_pos - v_pos) <= distance_cutoff:
                    for site in site_dict[ac][s_pos]:
                        site_list.append("%s:%s:%s" % (ac,s_pos,site))
        record_list.append({"variant":val, "sitelist":site_list})

    ts_format = "%Y-%m-%d %H:%M:%S %Z%z"
    ts = datetime.datetime.now(pytz.timezone('US/Eastern')).strftime(ts_format)
    list_id = "" if len(record_list) == 0 else list_id
    if len(record_list) != 0:
        cache_info = {
            "query":query_obj,
            "ts":ts,
            "record_type":record_type,
            "search_type":"site_search",
            "cache_name":"mcp_variants_mapped"
        }
        cache_hitlist(dbh,list_id,record_list,cache_info,cache_coll,config_obj)
    
    res_obj = {
        "site_result_id":query_obj["site_result_id"],
        "variant_result_id":query_obj["variant_result_id"],
        "result_id":result_id,
        "resultcount":len(record_list),
        "source":"new"
    }

    return res_obj
    

def get_cached(query_obj, config_obj):

    dbh, error_obj = get_mongodb()
    if error_obj != {}:
        return error_obj

    error_list = get_errors_in_query("mcp_get_cached",query_obj, config_obj)
    if error_list != []:
        return {"error_list":error_list}

    res_obj = {"results":[]}
    cache_coll = "c_usercache"
    mongo_query = {"list_id":query_obj["list_id"]}
    for cached_obj in dbh[cache_coll].find(mongo_query):
        res_obj["results"] += cached_obj["results"]
    

    return res_obj


                            



