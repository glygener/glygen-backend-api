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





def cart_list(query_obj, config_obj):

    dbh, error_obj = get_mongodb()
    if error_obj != {}:
        return error_obj


    #Collect errors 
    error_list = get_errors_in_query("cart_list", query_obj, config_obj)
    if error_list != []:
        return {"error_list":error_list}
    cache_collection = "c_listcache"


    #Get cached object
    mongo_query = {}
    if "id" in query_obj:
        mongo_query["list_id"] = query_obj["id"]
    cached_obj = dbh[cache_collection].find_one(mongo_query)
    #check for post-access error, error_list should be empty upto this line
    if cached_obj == None:
        return {"error_list":[{"error_code":"non-existent-search-results"}]}

    recordtype2idfield = {
        "glycan":"glytoucan_ac",
        "protein":"uniprot_canonical_ac"
    }
    if query_obj["type"] not in recordtype2idfield:
        return {"error_list":[{"error_code":"record-type-not-supported"}]}
    
    id_field = recordtype2idfield[query_obj["type"]]

    res_obj = []
    for doc in dbh[cache_collection].find(mongo_query):
        #for record_id in doc["results"]:
        for obj in doc["results"]:
            res_obj.append({"id":obj[id_field]})

    return res_obj










