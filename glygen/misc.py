import os,sys
from flask_restx import Namespace, Resource, fields
from flask import (request, current_app, send_file)
from glygen.document import get_one, get_many, insert_one, update_one, delete_one, order_json_obj
from werkzeug.utils import secure_filename
import datetime
import time
import pytz
import subprocess
import json
import bcrypt
import pymongo
import requests

from glygen.db import get_mongodb, log_error

from glygen.misc_apilib import validate, propertylist, pathlist, messagelist, verlist, gtclist, bcolist
from glygen.util import get_req_obj, get_filter_conf, make_list_objects_indirect, apply_pagination
from glygen.auth_apilib import create_github_issue
import traceback


from glygen.indexlib import search_one, search_all
from glygen.protein_apilib import protein_detail
from glygen.glycan_apilib import glycan_detail
from glygen.biomarker_apilib import biomarker_detail
from glygen.disease_apilib import disease_detail

from glygen.protein_apilib import search_simple as protein_search_simple
from glygen.glycan_apilib import search_simple as glycan_search_simple
from glygen.biomarker_apilib import search_simple as biomarker_search_simple
from glygen.disease_apilib import search_simple as disease_search_simple


from glygen.globalsearch_apilib import globalsearch_search


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
            for k in ["GITHUB_TOKEN", "GITHUB_ASSIGNEE", "SERVER", "DATA_PATH", "DB_NAME", "MAIL_SERVER", "MAIL_PORT", "MAIL_SENDER"]:
                if k in os.environ:
                    res_obj["config"][k] = os.environ[k]
                if k in current_app.config:
                    res_obj["config"][k] = current_app.config[k]
            #return res_obj
 
            mongo_dbh, error_obj = get_mongodb()
            res_obj["connection_status"] = "success" if error_obj == {} else error_obj
            #return res_obj
    
            res_obj["user_agent"] = request.headers.get('User-Agent')
            res_obj["referer"] = request.headers.get('referer')
            res_obj["origin"] = request.headers.get('Origin')
            return res_obj
            
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





@api.route('/get_object/')
class Misc(Resource):
    @api.doc(False)
    def post(self):
        start_ts = datetime.datetime.now(pytz.timezone('US/Eastern'))
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        json_url = os.path.join(SITE_ROOT, "conf/filter_init.json")
        config_obj["filter_init"] = json.load(open(json_url))
        
        res_obj = {}
        try:
            req_obj = get_req_obj(request)
            # objects are placed in local disk space (/local/glygen/testdb/)
            # to avoid I/O issue ... this path needs to be mounted to 
            # the API container
            if req_obj["mode"] == "filesystem":
                testdb_path = config_obj["perf_test"]["testdb_path"]
                file_path = "%s%s.json" % (testdb_path, req_obj["id"])
                res_obj = {"error_list":["file-not-found"]}
                if os.path.isfile(file_path):
                    res_obj = json.load(open(file_path))
            elif req_obj["mode"] in ["mongodb", "mongodb-pagination"]:
                id_field, record_id = req_obj["id_field"], req_obj["id"]
                q = {id_field:record_id}
                if "pagination" in req_obj:
                    for k in req_obj["pagination"]:
                        q[k] = req_obj["pagination"][k]
                res_obj = protein_detail(q, config_obj)
        except Exception as e:
            res_obj = log_error(traceback.format_exc())
        http_code = 500 if "error_list" in res_obj else 200
        
        end_ts = datetime.datetime.now(pytz.timezone('US/Eastern'))

        ts_format = "%Y-%m-%d %H:%M:%S %Z%z"
        start_ts_f = start_ts.strftime(ts_format)
        end_ts_f = end_ts.strftime(ts_format)
        elapsed = str(end_ts - start_ts)
        
        res_obj = {
            "api_overhead":{"start_ts":start_ts_f, "end_ts":end_ts_f, "elapsed":elapsed},
            "record":res_obj
        }

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





@api.route('/apitest/')
class Misc(Resource):
    @api.doc(False)
    def post(self):
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        res_obj = {}
        try:

            start_ts = datetime.datetime.now(pytz.timezone('US/Eastern'))
            req_obj = get_req_obj(request)
            mode = req_obj["mode"] if "mode" in req_obj else ""
            if "name" not in req_obj or "payload" not in req_obj:
                res_obj["error_list"] = [{"error":"incomplete set of parameters"}]
            else:
                if req_obj["name"].find("_search_simple") != -1:
                    if mode == "old":
                        if req_obj["name"] == "protein_search_simple":
                            res_obj = protein_search_simple(req_obj["payload"], config_obj)
                        elif req_obj["name"] == "glycan_search_simple":
                            res_obj = glycan_search_simple(req_obj["payload"], config_obj)
                        elif req_obj["name"] == "biomarker_search_simple":
                            res_obj = biomarker_search_simple(req_obj["payload"], config_obj)
                        elif req_obj["name"] == "disease_search_simple":
                            res_obj = disease_search_simple(req_obj["payload"], config_obj)
                    else:
                        cache_flag, exact_match_flag = False, False
                        res_obj = search_one(req_obj["name"], req_obj["payload"], config_obj,cache_flag,exact_match_flag)
                elif req_obj["name"] in ["globalsearch_search"]:
                    if mode == "old":
                        res_obj = globalsearch_search(req_obj["payload"], config_obj)
                    else:
                        res_obj = search_all(req_obj["name"], req_obj["payload"], config_obj)
                elif req_obj["name"].find("_detail") != -1:
                    if req_obj["name"] == "protein_detail":
                        res_obj = protein_detail(req_obj["payload"], config_obj)
                    elif req_obj["name"] == "glycan_detail":
                        res_obj = glycan_detail(req_obj["payload"], config_obj)
                    elif req_obj["name"] == "biomarker_detail":
                        res_obj = biomarker_detail(req_obj["payload"], config_obj)
                    elif req_obj["name"] == "disease_detail":
                        res_obj = disease_detail(req_obj["payload"], config_obj)
                elif req_obj["name"].find("_list") != -1:
                    res_obj = make_list_objects_indirect(req_obj["payload"], config_obj, False)
                    if "results" in res_obj:
                        res_obj["results"] = apply_pagination(res_obj["results"], req_obj)
                else:
                    res_obj["error_list"] = [{"error":"api=%s not supported" % (req_obj["name"])}]
            end_ts = datetime.datetime.now(pytz.timezone('US/Eastern'))
            elapsed = end_ts - start_ts
            secs = round(elapsed.total_seconds(), 2)
            ts_format = "%Y-%m-%d %H:%M:%S %Z%z"
            start_f = start_ts.strftime(ts_format)
            end_f = end_ts.strftime(ts_format)
            res_obj["api_latency"] = {"api_start":start_f,"api_end":end_f,"api_elapsed_seconds":secs} 
        except Exception as e:
            res_obj = log_error(traceback.format_exc())
        http_code = 500 if "error_list" in res_obj else 200
        return res_obj, http_code
    @api.doc(False)
    def get(self):
        return self.post()


