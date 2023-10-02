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




def pagination_page(query_obj, config_obj):

    dbh, error_obj = get_mongodb()
    if error_obj != {}:
        return error_obj

    #Collect errors 
    error_list = get_errors_in_query("pagination_page", query_obj, config_obj)
    if error_list != []:
        return {"error_list":error_list}

    main_id_dict = {
        "protein":"uniprot_canonical_ac",
        "glycan":"glytoucan_ac",
        "publication":"record_id",
        "biomarker":"biomarker_id"
    }

    record_type, record_id = query_obj["record_type"], query_obj["record_id"]
    main_id_field = main_id_dict[record_type]
    mongo_query = {main_id_field:{"$regex":record_id, "$options":"i"}}
    #return mongo_query

    collection = "c_" + record_type
    doc = dbh[collection].find_one(mongo_query)
   
     
    #check for post-access error, error_list should be empty upto this line
    post_error_list = []
    if doc == None:
        post_error_list.append({"error_code":"non-existent-record"})
        return {"error_list":post_error_list}


    # Get section objects if this record was batched 
    q = {"recordid": record_id, "recordtype": record_type}
    tmp_dict = {}
    for batch_doc in dbh["c_batch"].find(q):
        for sec in batch_doc["sections"]:
            if sec not in tmp_dict:
                tmp_dict[sec] = []
            if sec in doc:
                tmp_dict[sec] += batch_doc["sections"][sec]
    for sec in tmp_dict:
        doc[sec] = tmp_dict[sec]

    #return tmp_dict
   
     
    table_id = query_obj["table_id"]
    sec = table_id
    #sec = table_id.split("_")[0] if table_id.find("glycosylation_") != -1 else sec
    #sec = table_id.split("_")[0] if table_id.find("snv_") != -1 else sec
    #sec = table_id.split("_")[0] if table_id.find("expression_") != -1 else sec
    section_list = [sec]
 
    if "_id" in doc:
        doc.pop("_id")

    q = {"paginated_tables":[query_obj]}
    sec_tables = get_paginated_sections(doc, q, section_list)
   
    #return sec_tables

    if "error_list" in sec_tables:
        return sec_tables
    
    sec = table_id.split("_")[0] if table_id.find("glycosylation_") != -1 else sec
    sec = table_id.split("_")[0] if table_id.find("snv_") != -1 else sec
    sec = table_id.split("_")[0] if table_id.find("expression_") != -1 else sec
    if sec not in sec_tables:
        sec_tables[sec] = []
 
    res_obj = {"query":query_obj, "results":sec_tables[sec]}    
    return res_obj















