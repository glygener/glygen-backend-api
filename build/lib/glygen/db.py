import os
import pymongo
import datetime
import string
import pytz
import sqlite3
import random
import traceback
import json

import click
from flask import current_app, g
from flask.cli import with_appcontext


def get_mongodb():

    ret_obj, error_obj = {}, {}
<<<<<<< HEAD
    try: 
        conn_str, db_name = os.environ['MONGODB_CONNSTRING'], os.environ['DB_NAME']
        client = pymongo.MongoClient(conn_str)
        client.server_info()
        ret_obj = client[db_name]
=======
    try: #Connect to mongodb
        client = pymongo.MongoClient(
            current_app.config["DB_HOST"],
            authSource=current_app.config["DB_NAME"],
            username=current_app.config["DB_USERNAME"],
            password=current_app.config["DB_PASSWORD"],
            authMechanism='SCRAM-SHA-1',
            serverSelectionTimeoutMS=10000
        )
        client.server_info()
        ret_obj = client[current_app.config["DB_NAME"]]
>>>>>>> b661168d86f050c4e3f5b0a0708b45922caf2f3b
    except pymongo.errors.ServerSelectionTimeoutError as err:
        error_obj = {"status":0, "error":"Connection to MongoDB failed", "details":err.details}
    except pymongo.errors.OperationFailure as err:
        error_obj = {"status":0, "error":"Connection to MongoDB failed", "details":err.details}
    return ret_obj, error_obj



def log_error(error_log):

    mongo_dbh, error_obj = get_mongodb()
    if error_obj != {}:
        return error_obj
    ts_format = "%Y-%m-%d %H:%M:%S %Z%z"
    ts = datetime.datetime.now(pytz.timezone('US/Eastern')).strftime(ts_format)
    try:
        error_id = get_random_string(6)
        error_obj = {"id":error_id, "log":error_log, "ts":ts}
        res = mongo_dbh["c_log"].insert_one(error_obj)
        return {"status":0, "error":"exception-error-" + error_id}
    except Exception as e:
        return {"status":0, "error":"Unable to log error!"}



def get_random_string(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def reset_sequence_value(coll_obj, sequence_name):
    seq_doc = coll_obj.find_and_modify(
        query={'sequence_name': sequence_name},
        update={'$set': {'sequence_value': 0}},
        upsert=True,
        new=True
    )
    return


def next_sequence_value(coll_obj, sequence_name):
    seq_doc = coll_obj.find_and_modify(
        query={'sequence_name': sequence_name},
        update={'$inc': {'sequence_value': 1}},
        upsert=True,
        new=True
    )
    return int(seq_doc["sequence_value"])









def get_userinfo(user_name):

    try:
        mongo_dbh, error_obj = get_mongodb()
        user_doc = mongo_dbh["c_users"].find_one({'email' : user_name })
        user_info = {
            "fname":user_doc["fname"],
            "lname":user_doc["lname"],
            "email":user_doc["email"],
            "status":user_doc["status"]
        }
        return user_info, {}, 1
    except Exception as e:
        err_obj =  log_error(traceback.format_exc())
        return {}, err_obj, 0

