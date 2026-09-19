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
from glygen.util import get_errors_in_query


def structure_detail(query_obj, config_obj):

    dbh, error_obj = get_mongodb()
    if error_obj != {}:
        return error_obj

    #Collect errors 
    error_list = get_errors_in_query("structure_detail", query_obj, config_obj)
    if error_list != []:
        return {"error_list":error_list}
    collection = "c_structure"
    mongo_query = {"record_id":{"$eq":query_obj["structure_id"]}}
    doc = dbh[collection].find_one(mongo_query)
    
    #check for post-access error, error_list should be empty upto this line
    post_error_list = []
    if doc == None:
        post_error_list.append({"error_code":"non-existent-record"})
        return {"error_list":post_error_list}
    if "_id" in doc:
        doc.pop("_id")
    

    return doc







