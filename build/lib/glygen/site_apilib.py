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



def site_search_init(config_obj):
    
    dbh, error_obj = get_mongodb()
    if error_obj != {}:
        return error_obj

    collection = "c_searchinit"
    doc =  dbh[collection].find_one({})

    res_obj = doc["site"]
    
    return res_obj




def site_detail(query_obj, config_obj):
     
    dbh, error_obj = get_mongodb()
    if error_obj != {}:
        return error_obj

    #Collect errors 
    error_list = get_errors_in_query("site_detail", query_obj, config_obj)
    if error_list != []:
        return {"error_list":error_list}


    collection = "c_protein"
    id_parts = query_obj["site_id"].split(".")
    if len(id_parts) != 3:
        return {"error_list":[{"error_code":"invalid-site-id:%s" % (query_obj["site_id"])}]}
 
    canon,start_pos, end_pos = id_parts[0], id_parts[1], id_parts[2]
    mongo_query = {"uniprot_canonical_ac":canon}
    if canon.find("-") == -1:
        mongo_query = {"uniprot_ac":canon}
    canon_doc = dbh[collection].find_one(mongo_query)

    post_error_list = []
    if canon_doc == None:
        post_error_list.append({"error_code":"non-existent-record"})
        return {"error_list":post_error_list}
       
 
    collection = "c_site"
    mongo_query = {"id":query_obj["site_id"]}
    obj = dbh[collection].find_one(mongo_query)
    if obj == None and canon_doc != None:
        canon = canon_doc["uniprot_canonical_ac"]
        mongo_query = {"id":"%s.%s.%s" % (canon, start_pos, end_pos)}
        obj = dbh[collection].find_one(mongo_query)

    #check for post-access error, error_list should be empty upto this line
    if obj == None:
        post_error_list.append({"error_code":"non-existent-record"})
        return {"error_list":post_error_list}
    if "_id" in obj:
        obj.pop("_id")


    url = config_obj["urltemplate"]["uniprot"] % (canon_doc["uniprot_canonical_ac"])
    obj["uniprot_id"] = canon_doc["uniprot_id"] if "uniprot_id" in canon_doc else ""
    obj["uniprot"] = {
        "uniprot_canonical_ac":canon_doc["uniprot_canonical_ac"], 
        "uniprot_id":canon_doc["uniprot_id"],
        "url":url,
        "length": canon_doc["sequence"]["length"]
    }
    for k in ["uniprot","sequence","mass", "protein_names", "gene", "gene_names","species",
            "refseq"]:
        if k in canon_doc and k not in obj:
            obj[k] = canon_doc[k]


    if "paginated_tables" in query_obj:
        table_id_list = []
        for o in query_obj["paginated_tables"]:
            if o["table_id"] not in table_id_list:
                table_id_list.append(o["table_id"])
        sec_tables = get_paginated_sections(obj, query_obj, table_id_list, True)
        if "error_list" in sec_tables:
            return sec_tables
        for sec in sec_tables:
            obj[sec] = sec_tables[sec]

    return obj



def site_search(query_obj, config_obj):

    dbh, error_obj = get_mongodb()
    if error_obj != {}:
        return error_obj


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


    tissue_id, tissue_name, tax_id = "", "", ""
    if "set_name" in query_obj and "tissue_id" in query_obj and "tax_id" in query_obj:
        tissue_id, tax_id = query_obj["tissue_id"], query_obj["tax_id"]

    result_id = query_obj["set_name"] + "." + list_id
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
    if "set_name" in query_obj and "tissue_id" in query_obj and "tax_id" in query_obj:
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
                if query_obj["set_name"] == "glycosites_experimental":
                    for obj in doc["glycosylation"]:
                        cat = obj["site_category"] if "site_category" in obj else ""
                        if "start_pos" in obj and cat.find("reported") != -1:
                            if obj["start_pos"] > 1 and obj["start_pos"] == obj["end_pos"]:
                                site = "%s:%s:%s" % (ac, obj["start_pos"], obj["start_aa"])
                                tmp_dict[site] = True
                elif query_obj["set_name"] == "disease_variants":
                    for obj in doc["snv"]:
                        if "start_pos" in obj and "disease" in obj["keywords"]:
                            if obj["start_pos"] > 1 and obj["start_pos"] == obj["end_pos"]:
                                ref_aa, alt_aa = obj["sequence_org"], obj["sequence_mut"]
                                site = "%s:%s:%s>%s" % (ac, obj["start_pos"], ref_aa, alt_aa)
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
            "search_type":"site_search"
        }
        cache_hitlist(dbh,list_id,record_list,cache_info,cache_coll,config_obj)
    res_obj = {
        "tissue_id":query_obj["tissue_id"],
        "tissue_name":query_obj["tissue_name"],
        "tax_id":query_obj["tax_id"],
        "result_id":result_id, 
        "resultcount":len(record_list), 
        "source":"new"
    }
    
    return res_obj




