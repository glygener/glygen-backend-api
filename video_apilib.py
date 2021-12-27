import os
import string
import random
import hashlib
import json
import commands
import datetime,time
import bcrypt
import base64
import pytz
from collections import OrderedDict
from bson.objectid import ObjectId


import auth_apilib 

import smtplib
from email.mime.text import MIMEText
import errorlib
import util



def video_addnew(query_obj, config_obj):

    db_obj = config_obj[config_obj["server"]]["dbinfo"]
    dbh, error_obj = util.connect_to_mongodb(db_obj) #connect to mongodb
    if error_obj != {}:
        return error_obj

    #Collect errors 
    error_list = errorlib.get_errors_in_query("video_addnew",query_obj, config_obj)
    if error_list != []:
        return {"error_list":error_list}

    res_obj = auth_apilib.auth_tokenstatus({"token":query_obj["token"]}, config_obj)
    
    #check validity of token
    if "error_list" in res_obj:
        return res_obj
    if "status" not in res_obj:
        return {"error_list":[{"error_code":"invalid-token"}]}
    if res_obj["status"] != 1:
        return {"error_list":[{"error_code":"invalid-token"}]}

    #check write-access
    user_info = dbh["c_users"].find_one({'email' : res_obj["email"].lower()})
    if "access" not in user_info:
        return {"error_list":[{"error_code":"no-write-access"}]}
    if user_info["access"] != "write":
        return {"error_list":[{"error_code":"no-write-access"}]}

    res_obj = {}
    try:
        #Always keep only one document
        res = dbh["c_video"].delete_many({})
        query_obj.pop("token")
        query_obj["createdts"] = datetime.datetime.now()
        res = dbh["c_video"].insert_one(query_obj)
        res_obj = {"type":"success"}
    except Exception as e:
        res_obj = {"error_list":[{"error_code":str(e)}]}

    return res_obj




def video_detail(query_obj, config_obj):

    db_obj = config_obj[config_obj["server"]]["dbinfo"]
    dbh, error_obj = util.connect_to_mongodb(db_obj) #connect to mongodb
    if error_obj != {}:
        return error_obj

    #Collect errors 
    error_list = errorlib.get_errors_in_query("video_detail",query_obj, config_obj)
    if error_list != []:
        return {"error_list":error_list}
   
    res_obj = auth_apilib.auth_tokenstatus({"token":query_obj["token"]}, config_obj)
    
    #check validity of token
    if "error_list" in res_obj:
        return res_obj
    if "status" not in res_obj:
        return {"error_list":[{"error_code":"invalid-token"}]}
    if res_obj["status"] != 1:
        return {"error_list":[{"error_code":"invalid-token"}]}

    res_obj = {}
    try:
        q_obj = {}
        doc_list = list(dbh["c_video"].find(q_obj))
        res_obj = doc_list[0]
        if res_obj == None:
            return {"error_list":[{"error_code":"record-not-found"}]}
        res_obj["id"] = str(res_obj["_id"])
        res_obj.pop("_id")
        for k in ["createdts"]:
            if k not in res_obj:
                continue
            res_obj[k] = res_obj[k].strftime('%Y-%m-%d %H:%M:%S %Z%z')
    except Exception as e:
        res_obj = {"error_list":[{"error_code":str(e)}]}

    return res_obj

    




def video_list(query_obj, config_obj):

    db_obj = config_obj[config_obj["server"]]["dbinfo"]
    path_obj = config_obj[config_obj["server"]]["pathinfo"]
    dbh, error_obj = util.connect_to_mongodb(db_obj) #connect to mongodb

    #Collect errors 
    error_list = errorlib.get_errors_in_query("video_list",query_obj, config_obj)
    if error_list != []:
        return {"error_list":error_list}

    res_obj = auth_apilib.auth_tokenstatus({"token":query_obj["token"]}, config_obj)
    if "error_list" in res_obj:
        return res_obj
    if "status" not in res_obj:
        return {"error_list":[{"error_code":"invalid-token"}]}
    if res_obj["status"] != 1:
        return {"error_list":[{"error_code":"invalid-token"}]}
    


    import pymongo
    res_obj = []
    try:
        cond_list = []
        cond_list.append({"visibility":{"$eq":"visible"}})
        q_obj = {} if cond_list == [] else  {"$and":cond_list}
        doc_list = dbh["c_video"].find(q_obj).sort('createdts', pymongo.DESCENDING)
        for doc in doc_list:
            doc["id"] = str(doc["_id"])
            doc.pop("_id")
            for k in ["createdts", "updatedts", "start_date", "end_date"]:
                if k not in doc:
                    continue
                doc[k] = doc[k].strftime('%Y-%m-%d %H:%M:%S %Z%z')
            res_obj.append(doc)
    except Exception as e:
        res_obj = {"error_list":[{"error_code":str(e)}]}


    return res_obj



def video_delete(query_obj, config_obj):

    db_obj = config_obj[config_obj["server"]]["dbinfo"]
    path_obj = config_obj[config_obj["server"]]["pathinfo"]
    dbh, error_obj = util.connect_to_mongodb(db_obj) #connect to mongodb

    #Collect errors 
    error_list = errorlib.get_errors_in_query("video_delete",query_obj, config_obj)
    if error_list != []:
        return {"error_list":error_list}

    res_obj = auth_apilib.auth_tokenstatus({"token":query_obj["token"]}, config_obj)

    #check validity of token
    if "error_list" in res_obj:
        return res_obj
    if "status" not in res_obj:
        return {"error_list":[{"error_code":"invalid-token"}]}
    if res_obj["status"] != 1:
        return {"error_list":[{"error_code":"invalid-token"}]}

    #check write-access
    user_info = dbh["c_users"].find_one({'email' : res_obj["email"].lower()})
    if "access" not in user_info:
        return {"error_list":[{"error_code":"no-write-access"}]}
    if user_info["access"] != "write":
        return {"error_list":[{"error_code":"no-write-access"}]}


    res_obj = {}
    try:
        q_obj = {"_id":ObjectId(query_obj["id"])}
        doc = dbh["c_video"].find_one(q_obj)
        if doc == None:
            res_obj =  {"error_list":[{"error_code":"record-not-found"}]}
        else:
            update_obj = {"visibility":"hidden"}
            res = dbh["c_video"].update_one(q_obj, {'$set':update_obj}, upsert=True)
            res_obj = {"type":"success"}
    except Exception as e:
        res_obj = {"error_list":[{"error_code":str(e)}]}

    return res_obj

