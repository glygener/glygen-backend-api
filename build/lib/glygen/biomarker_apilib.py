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





def biomarker_detail(query_obj, config_obj):

    dbh, error_obj = get_mongodb()
    if error_obj != {}:
        return error_obj


    #Collect errors 
    error_list = get_errors_in_query("biomarker_detail", query_obj, config_obj)
    if error_list != []:
        return {"error_list":error_list}
    collection = "c_biomarker"

    mongo_query = {"biomarker_id":{"$eq":query_obj["id"]}}
    biomarker_doc = dbh[collection].find_one(mongo_query)
    #check for post-access error, error_list should be empty upto this line
    post_error_list = []
    if biomarker_doc == None:
        post_error_list.append({"error_code":"non-existent-record"})
        return {"error_list":post_error_list}


        
    if "paginated_tables" in query_obj:
        seen = {}
        for o in query_obj["paginated_tables"]:
            sec = o["table_id"]
            seen[sec] = True
        section_list = list(seen.keys())
        sec_tables = get_paginated_sections(biomarker_doc, query_obj, section_list)
        if "error_list" in sec_tables:
            return sec_tables
        for sec in seen:
            if sec in sec_tables:
                biomarker_doc[sec] = sec_tables[sec]



    clean_obj(biomarker_doc, config_obj["removelist"]["c_biomarker"], "c_biomarker")

    return biomarker_doc








