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

    clean_obj(biomarker_doc, config_obj["removelist"]["c_biomarker"], "c_biomarker")

    return biomarker_doc








