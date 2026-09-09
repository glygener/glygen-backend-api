import os
import json
import datetime,time
import pytz
from flask import (request, current_app)
from glygen.db import get_mongodb



def get_graph_record(query_obj, config_obj):

    dbh, error_obj = get_mongodb()
    if error_obj != {}:
        return error_obj

    collection = "c_graph"
    mongo_query = {"record_id":{'$eq': query_obj["record_id"]}}
    doc = dbh[collection].find_one(mongo_query)
    post_error_list = []
    if doc == None:
        post_error_list.append({"error_code":"non-existent-record"})
        res_obj = {"error_list":post_error_list}
        return res_obj
    if "_id" in doc:
        doc.pop("_id")
   
    return doc



