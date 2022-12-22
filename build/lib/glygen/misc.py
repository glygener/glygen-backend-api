import os,sys
from flask_restx import Namespace, Resource, fields
from flask import (request, current_app, send_file)
from glygen.document import get_one, get_many, insert_one, update_one, delete_one, order_json_obj
from werkzeug.utils import secure_filename
import datetime
import time
import subprocess
import json
import bcrypt
import pymongo
from flask_jwt_extended import (
    jwt_required, get_jwt_identity
)

from glygen.db import get_mongodb

from glygen.misc_apilib import validate, propertylist, pathlist, messagelist, verlist, gtclist, bcolist
from glygen.util import get_error_obj, trim_object
import traceback


api = Namespace("misc", description="Misc APIs")

validate_query_model = api.model(
    'Validate Query', { 'query': fields.String(required=True, default="", description='')})
propertylist_query_model = api.model(
    'Propertylist Query', { 'query': fields.String(required=True, default="", description='')})
pathlist_query_model = api.model(
    'Pathlist Query', { 'query': fields.String(required=True, default="", description='')})
messagelist_query_model = api.model(
    'Messagelist Query', { 'query': fields.String(required=True, default="", description='')})
verlist_query_model = api.model(
    'Verlist Query', { 'query': fields.String(required=True, default="", description='')})
gtclist_query_model = api.model(
    'Gtclist Query', { 'query': fields.String(required=True, default="", description='')})
bcolist_query_model = api.model(
    'Bcolist Query', { 'query': fields.String(required=True, default="", description='')})

info_query_model = api.model(
    'Info Query', { 'query': fields.String(required=True, default="", description='')})

lastid_query_model = api.model(
    'Last ID Query', { 'query': fields.String(required=True, default="", description='')})


@api.route('/info/')
class Misc(Resource):
    @api.doc('info')
    @api.expect(info_query_model)
    def post(self):
        api_name = "misc_info"
        res_obj = {"config":{}}
        try:
<<<<<<< HEAD
            mongo_dbh, error_obj = get_mongodb()
            res_obj["connection_status"] = "success" if error_obj == {} else error_obj
            for k in ["SERVER", "DATA_PATH", "DB_NAME", "MAIL_SERVER", "MAIL_PORT", "MAIL_SENDER"]:
                if k in os.environ:
                    res_obj["config"][k] = os.environ[k]
            
=======
            k_list = ["DB_HOST", "DB_NAME", "DB_USERNAME",  "DATA_PATH", "MAX_CONTENT_LENGTH"]
            for k in k_list:
                res_obj["config"][k] = current_app.config[k]
            mongo_dbh, error_obj = get_mongodb()
            res_obj["connection_status"] = "success" if error_obj == {} else error_obj
>>>>>>> b661168d86f050c4e3f5b0a0708b45922caf2f3b
            init_obj = mongo_dbh["c_init"].find_one({})
            if "_id" in init_obj:
                init_obj.pop("_id")
            res_obj["initobj"] = init_obj
        except Exception as e:
            log_path = current_app.config["LOG_PATH"]
            res_obj = get_error_obj(api_name, traceback.format_exc(), log_path)
        return res_obj


@api.route('/validate/')
class Misc(Resource):
    @api.doc('validate')
    @api.expect(validate_query_model)
    def post(self):
        api_name = "misc_validate"
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        res_obj = {}
        try:
            req_obj = request.json
            trim_object(req_obj)
<<<<<<< HEAD
            data_path = os.environ["DATA_PATH"]
=======
            data_path = current_app.config["DATA_PATH"]
>>>>>>> b661168d86f050c4e3f5b0a0708b45922caf2f3b
            res_obj = validate(req_obj, config_obj)
        except Exception as e:
            log_path = current_app.config["LOG_PATH"] 
            res_obj = get_error_obj(api_name, traceback.format_exc(), log_path)
        return res_obj

@api.route('/propertylist/')
class Misc(Resource):
    @api.doc('propertylist')
    @api.expect(propertylist_query_model)
    def post(self):
        api_name = "misc_propertylist"
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        res_obj = {}
        try:
            req_obj = request.json
            trim_object(req_obj)
<<<<<<< HEAD
            data_path = os.environ["DATA_PATH"]
=======
            data_path = current_app.config["DATA_PATH"]
>>>>>>> b661168d86f050c4e3f5b0a0708b45922caf2f3b
            res_obj = propertylist(req_obj, config_obj)
        except Exception as e:
            log_path = current_app.config["LOG_PATH"]
            res_obj = get_error_obj(api_name, traceback.format_exc(), log_path)
        return res_obj


@api.route('/pathlist/')
class Misc(Resource):
    @api.doc('pathlist')
    @api.expect(pathlist_query_model)
    def post(self):
        api_name = "misc_pathlist"
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        res_obj = {}
        try:
            req_obj = request.json
            trim_object(req_obj)
<<<<<<< HEAD
            data_path = os.environ["DATA_PATH"]
=======
            data_path = current_app.config["DATA_PATH"]
>>>>>>> b661168d86f050c4e3f5b0a0708b45922caf2f3b
            res_obj = pathlist(req_obj, config_obj)
        except Exception as e:
            log_path = current_app.config["LOG_PATH"]
            res_obj = get_error_obj(api_name, traceback.format_exc(), log_path)
        return res_obj

@api.route('/messagelist/')
class Misc(Resource):
    @api.doc('messagelist')
    @api.expect(messagelist_query_model)
    def post(self):
        api_name = "misc_messagelist"
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        res_obj = {}
        try:
            req_obj = request.json
            trim_object(req_obj)
<<<<<<< HEAD
            data_path = os.environ["DATA_PATH"]
=======
            data_path = current_app.config["DATA_PATH"]
>>>>>>> b661168d86f050c4e3f5b0a0708b45922caf2f3b
            res_obj = messagelist(config_obj)
        except Exception as e:
            log_path = current_app.config["LOG_PATH"]
            res_obj = get_error_obj(api_name, traceback.format_exc(), log_path)
        return res_obj


@api.route('/verlist/')
class Misc(Resource):
    @api.doc('verlist')
    @api.expect(verlist_query_model)
    def post(self):
        api_name = "misc_verlist"
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        res_obj = {}
        try:
            req_obj = request.json
            trim_object(req_obj)
<<<<<<< HEAD
            data_path = os.environ["DATA_PATH"]
=======
            data_path = current_app.config["DATA_PATH"]
>>>>>>> b661168d86f050c4e3f5b0a0708b45922caf2f3b
            res_obj = verlist(config_obj)
        except Exception as e:
            log_path = current_app.config["LOG_PATH"]
            res_obj = get_error_obj(api_name, traceback.format_exc(), log_path)
        return res_obj


@api.route('/gtclist/')
class Misc(Resource):
    @api.doc('gtclist')
    @api.expect(gtclist_query_model)
    def post(self):
        api_name = "misc_gtclist"
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        res_obj = {}
        try:
            req_obj = request.json
            trim_object(req_obj)
<<<<<<< HEAD
            data_path = os.environ["DATA_PATH"]
=======
            data_path = current_app.config["DATA_PATH"]
>>>>>>> b661168d86f050c4e3f5b0a0708b45922caf2f3b
            res_obj = gtclist(config_obj,data_path)
        except Exception as e:
            log_path = current_app.config["LOG_PATH"]
            res_obj = get_error_obj(api_name, traceback.format_exc(), log_path)
        return res_obj

@api.route('/bcolist/')
class Misc(Resource):
    @api.doc('bcolist')
    @api.expect(bcolist_query_model)
    def post(self):
        api_name = "misc_bcolist"
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        res_obj = {}
        try:
            req_obj = request.json
            trim_object(req_obj)
<<<<<<< HEAD
            data_path = os.environ["DATA_PATH"]
=======
            data_path = current_app.config["DATA_PATH"]
>>>>>>> b661168d86f050c4e3f5b0a0708b45922caf2f3b
            res_obj = bcolist(config_obj)
        except Exception as e:
            log_path = current_app.config["LOG_PATH"]
            res_obj = get_error_obj(api_name, traceback.format_exc(), log_path)
        return res_obj


@api.route('/lastid/')
class Misc(Resource):
    @api.doc('lastid')
    @api.expect(lastid_query_model)
    def post(self):
        api_name = "misc_lastid"
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        res_obj = {}
        try:
            req_obj = request.json
            dbh, error_obj = get_mongodb()
            if error_obj != {}:
                return error_obj
            p_dict = {
                "c_job":"jobid",
                "c_video":"_id",
                "c_event":"_id"
            }
            res_obj = {}
            
            sort_obj = [("_id",pymongo.DESCENDING)]
            for coll in p_dict:
                p = p_dict[coll]
                for doc in dbh[coll].find({}).sort(sort_obj):
                    val = str(doc[p]) if p == "_id" else doc[p]
                    res_obj[coll] = {p:val}
                    break
        except Exception as e:
            log_path = current_app.config["LOG_PATH"]
            res_obj = get_error_obj(api_name, traceback.format_exc(), log_path)
        return res_obj




