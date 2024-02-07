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
import requests

from glygen.db import get_mongodb, log_error

from glygen.misc_apilib import validate, propertylist, pathlist, messagelist, verlist, gtclist, bcolist
from glygen.util import get_req_obj, get_filter_conf
from glygen.auth_apilib import create_github_issue

import traceback


api = Namespace("misc", description="Misc APIs")

verlist_query_model = api.model("Misc Version List Query", {})
gtclist_query_model = api.model("Misc GlyTouCan Accession List Query", {})


@api.route('/info/')
class Misc(Resource):
    @api.doc(False)
    def post(self):
        res_obj = {"config":{}}
        try:
            #ip_addr = request.remote_addr
            #ip_addr = request.environ['REMOTE_ADDR']
            #ip_addr = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
            #return {"ip":ip_addr}
            mongo_dbh, error_obj = get_mongodb()
            res_obj["connection_status"] = "success" if error_obj == {} else error_obj
            for k in ["GITHUB_TOKEN", "GITHUB_ASSIGNEE", "SERVER", "DATA_PATH", "DB_NAME", "MAIL_SERVER", "MAIL_PORT", "MAIL_SENDER"]:
                if k in os.environ:
                    res_obj["config"][k] = os.environ[k]
                if k in current_app.config:
                    res_obj["config"][k] = current_app.config[k]
            
            init_obj = mongo_dbh["c_init"].find_one({})
            if "_id" in init_obj:
                init_obj.pop("_id")
            res_obj["initobj"] = init_obj
        except Exception as e:
            res_obj = log_error(traceback.format_exc())
        http_code = 500 if "error_list" in res_obj else 200
        return res_obj, http_code


@api.route('/github/')
class Misc(Resource):
    @api.doc(False)
    def post(self):
        res_obj = {"config":{}}
        try:
            github_endpoint = "https://api.github.com/repos/glygener/glygen-issues/issues"
            auth_token = "xxxx"
            issue_obj = {
                "title":" ... frontend user issue",
                "body":"body of frontend user issue",
                "assignees":["rykahsay"],
                "labels":["fronten_user_issue"]
            }
            res_obj = create_github_issue(github_endpoint, auth_token, issue_obj)
        except Exception as e:
            res_obj = log_error(traceback.format_exc())
        http_code = 500 if "error_list" in res_obj else 200
        return res_obj, http_code



@api.route('/validate/')
class Misc(Resource):
    @api.doc(False)
    def post(self):
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        res_obj = {}
        try:
            req_obj = get_req_obj(request)
            data_path = os.environ["DATA_PATH"]
            res_obj = validate(req_obj, config_obj)
        except Exception as e:
            res_obj = log_error(traceback.format_exc())
        http_code = 500 if "error_list" in res_obj else 200
        return res_obj, http_code

@api.route('/propertylist/')
class Misc(Resource):
    @api.doc(False)
    def post(self):
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        res_obj = {}
        try:
            req_obj = get_req_obj(request)
            data_path = os.environ["DATA_PATH"]
            res_obj = propertylist(req_obj, config_obj)
        except Exception as e:
            res_obj = log_error(traceback.format_exc())
        http_code = 500 if "error_list" in res_obj else 200
        return res_obj, http_code


@api.route('/pathlist/')
class Misc(Resource):
    @api.doc(False)
    def post(self):
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        res_obj = {}
        try:
            req_obj = get_req_obj(request)
            data_path = os.environ["DATA_PATH"]
            res_obj = pathlist(req_obj, config_obj)
        except Exception as e:
            res_obj = log_error(traceback.format_exc())
        http_code = 500 if "error_list" in res_obj else 200
        return res_obj, http_code

@api.route('/messagelist/')
class Misc(Resource):
    @api.doc(False)
    def post(self):
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        res_obj = {}
        try:
            req_obj = get_req_obj(request)
            data_path = os.environ["DATA_PATH"]
            res_obj = messagelist(config_obj)
        except Exception as e:
            res_obj = log_error(traceback.format_exc())
        http_code = 500 if "error_list" in res_obj else 200
        return res_obj, http_code


@api.route('/verlist/')
class Misc(Resource):
    #@api.doc(False)
    @api.expect(verlist_query_model)
    def post(self):
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        res_obj = {}
        try:
            req_obj = {}
            data_path = os.environ["DATA_PATH"]
            res_obj = verlist(config_obj)
        except Exception as e:
            res_obj = log_error(traceback.format_exc())
        http_code = 500 if "error_list" in res_obj else 200
        return res_obj, http_code
    @api.doc(False)
    def get(self):
        return self.post()


@api.route('/gtclist/')
class Misc(Resource):
    #@api.doc(False)
    @api.expect(gtclist_query_model)
    def post(self):
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        res_obj = {}
        try:
            req_obj = {}
            data_path = os.environ["DATA_PATH"]
            res_obj = gtclist(config_obj,data_path)
        except Exception as e:
            res_obj = log_error(traceback.format_exc())
        http_code = 500 if "error_list" in res_obj else 200
        return res_obj, http_code
    @api.doc(False)
    def get(self):
        return self.post()


@api.route('/bcolist/')
class Misc(Resource):
    @api.doc(False)
    def post(self):
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        res_obj = {}
        try:
            req_obj = get_req_obj(request)
            data_path = os.environ["DATA_PATH"]
            res_obj = bcolist(config_obj)
        except Exception as e:
            res_obj = log_error(traceback.format_exc())
        http_code = 500 if "error_list" in res_obj else 200
        return res_obj, http_code
    @api.doc(False)
    def get(self):
        return self.post()



@api.route('/lastid/')
class Misc(Resource):
    @api.doc(False)
    def post(self):
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        res_obj = {}
        try:
            req_obj = get_req_obj(request)
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
            res_obj = log_error(traceback.format_exc())
        http_code = 500 if "error_list" in res_obj else 200
        return res_obj, http_code




