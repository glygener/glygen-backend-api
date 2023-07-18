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
from glygen.util import get_errors_in_query, sort_objects, order_obj, clean_obj, get_paginated_sections





def publication_detail(query_obj, config_obj):

    dbh, error_obj = get_mongodb()
    if error_obj != {}:
        return error_obj


    #Collect errors 
    error_list = get_errors_in_query("publication_detail", query_obj, config_obj)
    if error_list != []:
        return {"error_list":error_list}
    collection = "c_publication"


    #combo_id = "%s.%s" % (query_obj["type"].lower(), query_obj["id"])
    #mongo_query = {"record_id":{"$regex":combo_id, "$options":"i"}}
    mongo_query = {
        "$and":[
            {"reference.id":{"$eq":query_obj["id"]}},
            {"reference.type":{"$regex":query_obj["type"], "$options":"i"}}
        ]
    }
    
    publication_doc = dbh[collection].find_one(mongo_query)
    
    #check for post-access error, error_list should be empty upto this line
    post_error_list = []
    if publication_doc == None:
        post_error_list.append({"error_code":"non-existent-record"})
        return {"error_list":post_error_list}


    
    # Get section objects if this record was batched
    combo_id = "%s.%s" % (query_obj["type"].lower(), query_obj["id"])
    q = {"batchid": 1, "recordid": combo_id, "recordtype": "publication"}
    batch_doc = dbh["c_batch"].find_one(q)
    if batch_doc != None:
        for sec in batch_doc["sections"]:
            if sec in publication_doc:
                publication_doc[sec] += batch_doc["sections"][sec]

    

    if "paginated_tables" in query_obj:
        seen = {}
        for o in query_obj["paginated_tables"]:
            sec = o["table_id"].split("_")[0] if o["table_id"].find("glycosylation_") != -1 else o["table_id"]
            seen[sec] = True
        section_list = list(seen.keys())
        sec_tables = get_paginated_sections(publication_doc, query_obj, section_list)
        if "error_list" in sec_tables:
            return sec_tables
        for sec in sec_tables:
            publication_doc[sec] = sec_tables[sec]


    clean_obj(publication_doc, config_obj["removelist"]["c_publication"], "c_publication")

    return publication_doc




def get_section_objects(protein_doc, pub_doc):


    site_sec_list = ["snv", "glycosylation", "phosphorylation", "glycation", "mutagenesis"] 
    for sec in site_sec_list:
        if sec in protein_doc:
            for sec_obj in protein_doc[sec]:
                for ev_obj in sec_obj["evidence"]:
                    record_id = ""
                    if ev_obj["database"] != "":
                        record_id = "%s.%s" % (ev_obj["database"].lower(), ev_obj["id"])
                    if record_id == pub_doc["record_id"]:
                        if sec not in pub_doc:
                            pub_doc[sec] = []
                        sec_obj["uniprot_canonical_ac"] = protein_doc["uniprot_canonical_ac"]
                        pub_doc[sec].append(sec_obj)

    return







