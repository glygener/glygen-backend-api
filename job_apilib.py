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


def job_init(config_obj):

    #Set number of jobs allowed
    cmd = "%s -S %s" % (config_obj["jobinfo"]["tspath"], config_obj["jobinfo"]["maxjobs"])
    x = commands.getoutput(cmd)


    res_obj = {}
    for k_one in config_obj["jobinfo"]:
        if type(config_obj["jobinfo"][k_one]) is dict:
            if "paramlist" in config_obj["jobinfo"][k_one]:
                if k_one not in res_obj:
                    res_obj[k_one] = {"paramlist":[]}
                for obj in config_obj["jobinfo"][k_one]["paramlist"]:
                    res_obj[k_one]["paramlist"].append(obj)

    return res_obj


def job_addnew(query_obj, config_obj):


    db_obj = config_obj[config_obj["server"]]["dbinfo"]
    dbh, error_obj = util.connect_to_mongodb(db_obj) #connect to mongodb
    if error_obj != {}:
        return error_obj

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

   
    validation_obj, error_list = validate_input(query_obj, config_obj)
    if error_list != []:
        return {"error_list":error_list}


    res_obj = {}
    try:
        query_obj.pop("token")
        query_obj.pop("line_list")
        query_obj["jobid"] = 1
        if dbh["c_job"].find_one({"jobid":1}) != None:
            agg_obj = {"$group":{"_id":"","max_id":{"$max":"$jobid"}}}
            res = list(dbh["c_job"].aggregate([agg_obj]))
            query_obj["jobid"] = res[0]["max_id"] + 1

        in_dir = config_obj[config_obj["server"]]["pathinfo"]["userdata"]
        in_dir += "/" + str(query_obj["jobid"])
        cmd = "mkdir -p " + in_dir
        x = commands.getoutput(cmd)
        in_format = config_obj["jobinfo"][query_obj["jobtype"]]["informat"]
        out_format = config_obj["jobinfo"][query_obj["jobtype"]]["outformat"]
        in_file = in_dir + "/input." + in_format
        out_file = in_dir + "/output." + out_format
        with open(in_file, "w") as FW:
            FW.write("%s\n" % (validation_obj["buffer"]))
        cmd = "/usr/bin/md5sum " + in_file
        query_obj["md5sum"] = commands.getoutput(cmd).split(" ")[0]

        
        q_obj = {}
        for p in query_obj:
            if p not in ["token", "cmd", "status", "jobid"]:
                q_obj[p] = query_obj[p]
        old_doc = dbh["c_job"].find_one(q_obj)
        if old_doc != None:
            status_obj = update_job_status(dbh, old_doc, config_obj)
            if "error_list" in status_obj:
                return status_obj
            res_obj = {"submission":"old", "status":status_obj, "jobid":old_doc["jobid"]}
        else:
            if "incmdflag" in config_obj["jobinfo"][query_obj["jobtype"]]:
                in_cmdflag = config_obj["jobinfo"][query_obj["jobtype"]]["incmdflag"]
                query_obj["cmd"] += " %s %s" % (in_cmdflag, in_file)
            if "outcmdflag" in config_obj["jobinfo"][query_obj["jobtype"]]:
                out_cmdflag = config_obj["jobinfo"][query_obj["jobtype"]]["outcmdflag"]
                query_obj["cmd"] += " %s %s" % (out_cmdflag, out_file)
            
            job_lbl = "%s_%s" % (query_obj["jobtype"], query_obj["jobid"])
            cmd = "%s -E -L %s %s" % (config_obj["jobinfo"]["tspath"],job_lbl, query_obj["cmd"])
            query_obj["tsid"] = commands.getoutput(cmd).split(" ")[0]
            query_obj["status"] = get_job_status(query_obj["tsid"] , config_obj)
            inserted_id = dbh["c_job"].insert(query_obj)

            res_obj = {"submission":"new", "status":query_obj["status"], "jobid":query_obj["jobid"]}
    except Exception as e:
        res_obj = {"error_list":[{"error_code":str(e)}]}

    return res_obj


def job_queue(query_obj, config_obj):

    db_obj = config_obj[config_obj["server"]]["dbinfo"]
    dbh, error_obj = util.connect_to_mongodb(db_obj) #connect to mongodb
    if error_obj != {}:
        return error_obj

    res_obj = auth_apilib.auth_tokenstatus({"token":query_obj["token"]}, config_obj)

    #check validity of token
    if "error_list" in res_obj:
        return res_obj
    if "status" not in res_obj:
        return {"error_list":[{"error_code":"invalid-token"}]}
    if res_obj["status"] != 1:
        return {"error_list":[{"error_code":"invalid-token"}]}

    #Let's clear queue by removing finished jobs
    #cmd = "%s -C" % (config_obj["jobinfo"]["tspath"])
    #x = commands.getoutput(cmd)

    res_obj = {
        "header":["ID","State","Output","E-Level","Times(r/u/s)", "Command [run=3/3]"], 
        "rows":[]    
    }
    try:
        cmd = "%s" % (config_obj["jobinfo"]["tspath"])
        for line in commands.getoutput(cmd).split("\n")[1:]:
            row = []
            row.append(line[0:5].strip())
            row.append(line[5:16].strip())
            row.append(line[16:37].strip())
            row.append(line[37:46].strip())
            row.append(line[46:61].strip())
            row.append(line[61:].strip())
            res_obj["rows"].append(row)

    except Exception as e:
        res_obj = {"error_list":[{"error_code":str(e)}]}

    return res_obj


def job_status(query_obj, config_obj):

    db_obj = config_obj[config_obj["server"]]["dbinfo"]
    dbh, error_obj = util.connect_to_mongodb(db_obj) #connect to mongodb
    if error_obj != {}:
        return error_obj

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
        q_obj = {"jobid":query_obj["jobid"]}
        job_doc = dbh["c_job"].find_one(q_obj)
        if job_doc == None:
            return {"error_list":[{"error_code":"job-record-not-found"}]}
        #update job status
        status_obj = update_job_status(dbh, job_doc, config_obj)
        if "error_list" in status_obj:
            return status_obj
        res_obj = status_obj
        if res_obj["status"] == "finished":
            res_obj["output_files"] = []
            for f_obj in config_obj["jobinfo"][job_doc["jobtype"]]["output_files"]:
                url = "https://data.glygen.org"
                if config_obj["server"] in ["dev", "tst"]:
                    url = "https://data.%s.glygen.org" % (config_obj["server"])
                elif config_obj["server"] in ["beta"]:
                    url = "https://beta-data.glygen.org"
                url += "/ln2userdata/%s/%s/%s" % (config_obj["server"], job_doc["jobid"], f_obj["name"])
                o = {"format":f_obj["format"], "url":url}
                res_obj["output_files"].append(o)
    except Exception as e:
        res_obj = {"error_list":[{"error_code":str(e)}]}

    return res_obj
  


 
def job_detail(query_obj, config_obj):

    db_obj = config_obj[config_obj["server"]]["dbinfo"]
    dbh, error_obj = util.connect_to_mongodb(db_obj) #connect to mongodb
    if error_obj != {}:
        return error_obj

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
        q_obj = {"jobid":query_obj["jobid"]}
        res_obj = dbh["c_job"].find_one(q_obj)
        if res_obj == None:
            return {"error_list":[{"error_code":"record-not-found"}]}
       
        #update job status
        status_obj = update_job_status(dbh, res_obj, config_obj)
        if "error_list" in status_obj:
            return status_obj
        res_obj["status"] = status_obj

        res_obj["id"] = str(res_obj["_id"])
        res_obj.pop("_id")
        for k in ["createdts", "updatedts"]:
            if k not in res_obj:
                continue
            res_obj[k] = res_obj[k].strftime('%Y-%m-%d %H:%M:%S %Z%z')
    except Exception as e:
        res_obj = {"error_list":[{"error_code":str(e)}]}

    return res_obj


def job_list(query_obj, config_obj):

    db_obj = config_obj[config_obj["server"]]["dbinfo"]
    path_obj = config_obj[config_obj["server"]]["pathinfo"]
    dbh, error_obj = util.connect_to_mongodb(db_obj) #connect to mongodb

    #Collect errors 
    error_list = errorlib.get_errors_in_query("job_list",query_obj, config_obj)
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
        doc_list = dbh["c_job"].find({}).sort('createdts', pymongo.DESCENDING)
        for doc in doc_list:
            doc["id"] = str(doc["_id"])
            doc.pop("_id")
            for k in ["createdts", "updatedts"]:
                if k not in doc:
                    continue
                doc[k] = doc[k].strftime('%Y-%m-%d %H:%M:%S %Z%z')
            res_obj.append(doc)
    except Exception as e:
        res_obj = {"error_list":[{"error_code":str(e)}]}


    return res_obj


def job_update(query_obj, config_obj):

    db_obj = config_obj[config_obj["server"]]["dbinfo"]
    path_obj = config_obj[config_obj["server"]]["pathinfo"]
    dbh, error_obj = util.connect_to_mongodb(db_obj) #connect to mongodb


    #Collect errors 
    error_list = errorlib.get_errors_in_query("job_update",query_obj, config_obj)
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
        update_obj = {}
        for k in query_obj:
            if k not in ["token", "id"]:
                update_obj[k] = query_obj[k]
        res = dbh["c_job"].update_one(q_obj, {'$set':update_obj}, upsert=True)
        res_obj = {"type":"success"}
    except Exception as e:
        res_obj = {"error_list":[{"error_code":str(e)}]}


    return res_obj



def job_delete(query_obj, config_obj):

    db_obj = config_obj[config_obj["server"]]["dbinfo"]
    path_obj = config_obj[config_obj["server"]]["pathinfo"]
    dbh, error_obj = util.connect_to_mongodb(db_obj) #connect to mongodb

    #Collect errors 
    error_list = errorlib.get_errors_in_query("job_delete",query_obj, config_obj)
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
        doc = dbh["c_job"].find_one(q_obj)
        if doc == None:
            res_obj =  {"error_list":[{"error_code":"record-not-found"}]}
        else:
            update_obj = {"visibility":"hidden"}
            res = dbh["c_job"].update_one(q_obj, {'$set':update_obj}, upsert=True)
            res_obj = {"type":"success"}
    except Exception as e:
        res_obj = {"error_list":[{"error_code":str(e)}]}

    return res_obj




def validate_input(query_obj, config_obj):
   

    path_obj = config_obj[config_obj["server"]]["pathinfo"]
    release_dir = path_obj["datareleasespath"] + "data/v-%s/" % (config_obj["datarelease"])
    blastdb_dir = release_dir + "blastdb/"


    error_list = []
    if query_obj["jobtype"] not in config_obj["jobinfo"]:
        error_list.append({"error_code": "unknown job type"})
    elif "paramlist" not in config_obj["jobinfo"][query_obj["jobtype"]]:
        error_list.append({"error_code": "no paramters defined for job type"})
    else:
        query_obj["cmd"] = "%s" % (config_obj["jobinfo"][query_obj["jobtype"]]["path"])
        for obj in config_obj["jobinfo"][query_obj["jobtype"]]["paramlist"]:
            if obj["id"] in query_obj:
                if obj["type"] == "int":
                    query_obj[obj["id"]] = int(query_obj[obj["id"]])
                elif obj["type"] == "float":
                    query_obj[obj["id"]] = float(query_obj[obj["id"]])
                if "cmdflag" in obj:
                    val = query_obj[obj["id"]]
                    if query_obj["jobtype"] in ["blastp"] and obj["cmdflag"] == "-db":
                        val = blastdb_dir + val
                    query_obj["cmd"] += " %s %s" % (obj["cmdflag"], val)
        
    res_obj = {}
    res_obj["buffer"] = "\n".join(query_obj["line_list"]);
    #error_list.append({"error_code": "missing-%s" %(k),"concept":concept})

    return res_obj, error_list




def get_job_status(ts_id, config_obj):

    obj = {}
    cmd = "%s -s %s" % (config_obj["jobinfo"]["tspath"], ts_id)
    obj["status"] = commands.getoutput(cmd).split(" ")[0]
    cmd = "%s -i %s" % (config_obj["jobinfo"]["tspath"], ts_id)
    for line in commands.getoutput(cmd).split("\n"):
        k = line.split(":")[0].replace(" ", "_").lower()
        obj[k] = ":".join(line.split(":")[1:])
        obj[k] = obj[k].strip()
   
    
    return obj


def update_job_status(dbh, job_doc, config_obj):

    #If job is finished, don't do anything
    if "status" in job_doc:
        if job_doc["status"]["status"] == "finished":
            return job_doc["status"]

    res_obj = {}
    try:
        res_obj = get_job_status(job_doc["tsid"], config_obj)
        q_obj = {"jobid":job_doc["jobid"]}
        update_obj = {"status":res_obj}
        res = dbh["c_job"].update_one(q_obj, {'$set':update_obj}, upsert=True)
    except Exception as e:
        res_obj = {"error_list":[{"error_code":str(e)}]}

    return res_obj



    return obj


