import os
import string
import random
import hashlib
import json
import datetime,time
import pytz
from collections import OrderedDict


from glygen.db import get_mongodb
from glygen.util import cache_record_list, clean_obj, extract_name, get_errors_in_query, get_paginated_sections




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
    canon,start_pos, end_pos = query_obj["site_id"].split(".")
    mongo_query = {"uniprot_canonical_ac":canon}
    if canon.find("-") == -1:
        mongo_query = {"uniprot_ac":canon}
    canon_doc = dbh[collection].find_one(mongo_query)
    
    collection = "c_site"
    mongo_query = {"id":query_obj["site_id"]}
    site_doc = dbh[collection].find_one(mongo_query)
    if site_doc == None:
        canon = canon_doc["uniprot_canonical_ac"]
        mongo_query = {"id":"%s.%s.%s" % (canon, start_pos, end_pos)}
        site_doc = dbh[collection].find_one(mongo_query)

    #check for post-access error, error_list should be empty upto this line
    post_error_list = []
    if site_doc == None:
        post_error_list.append({"error_code":"non-existent-record"})
        return {"error_list":post_error_list}
    if "_id" in site_doc:
        site_doc.pop("_id")


    url = config_obj["urltemplate"]["uniprot"] % (canon_doc["uniprot_canonical_ac"])
    site_doc["uniprot_id"] = canon_doc["uniprot_id"] if "uniprot_id" in canon_doc else ""
    site_doc["uniprot"] = {
        "uniprot_canonical_ac":canon_doc["uniprot_canonical_ac"], 
        "uniprot_id":canon_doc["uniprot_id"],
        "url":url,
        "length": canon_doc["sequence"]["length"]
    }
    for k in ["uniprot","sequence","mass", "protein_names", "gene", "gene_names","species",
            "refseq"]:
        if k in canon_doc and k not in site_doc:
            site_doc[k] = canon_doc[k]


    
    if "paginated_tables" in query_obj:
        seen = {}
        for o in query_obj["paginated_tables"]:
            sec = o["table_id"].split("_")[0] if o["table_id"].find("glycosylation_") != -1 else o["table_id"]
            seen[sec] = True
        section_list = list(seen.keys())
        sec_tables = get_paginated_sections(site_doc, query_obj, section_list)
        if "error_list" in sec_tables:
            return sec_tables
        for sec in seen:
            if sec in sec_tables:
                site_doc[sec] = sec_tables[sec]


    return site_doc



