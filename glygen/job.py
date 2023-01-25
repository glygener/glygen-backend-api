import os,sys
from flask_restx import Namespace, Resource, fields
from flask import (request, current_app, send_file)
from glygen.db import log_error
from glygen.document import get_one, get_many, insert_one, update_one, delete_one, order_json_obj
from werkzeug.utils import secure_filename
import datetime
import time
import subprocess
import json
import bcrypt

from glygen.job_apilib import job_addnew, job_detail, job_update, job_list, job_delete,job_clean, job_results, job_status, job_queue, job_init

from glygen.util import trim_object
import traceback




api = Namespace("job", description="Job APIs")

PARAMS = api.model(
    "PARAMS",
    {
        "seq":fields.String(required=True, default="MSIQENISSLQLRSWVSKSQRDLAKSILIGAPGGPAGYLRRASVAQLTQELGTAFFQQQQLPAAMADTFLEHLCLLDIDSEPVAARSTSIIATIGPASRSVERLKEMIKAGMNIARLNFSQHAIAREAEAAVYHRQLFEELRRAAPLSRDPTEVTAIGAVEAAFKCCAAAIIVLTTT"),
        "targetdb":fields.String(required=True, default="canonicalsequences_all"),
        "num_alignments":fields.Integer(required=True, default=3),
        "evalue":fields.Float(required=True, default=1e-3)
    }
)

addnew_query_model = api.model(
    'Job Addnew Query', 
    { 
        "jobtype":fields.String(required=True, default="blastp"),
        "parameters":fields.Nested(PARAMS)
    }
)
detail_query_model = api.model(
    'Job Detail Query', 
    { 'jobid': fields.Integer(required=True, default=1)}
)

list_query_model = api.model(
    'Job List Query', 
    {
        "visibility":fields.String(required=True, default="all")
    }
)
update_query_model = api.model(
    'Job Update Query', 
    {
    }
)
delete_query_model = api.model(
    'Job Delete Query', 
    { 'jobid': fields.Integer(required=True, default=1)}
)   
results_query_model = api.model(
    'Job Results Query', 
    { 'jobid': fields.Integer(required=True, default=1)}
)

status_query_model = api.model(
    'Job Status Query',
    { 'jobid': fields.Integer(required=True, default=1)}
)   
clean_query_model = api.model('Job Clean Query', {})
queue_query_model = api.model('Job Queue Query', {})
init_query_model = api.model('Job Init Query', {})



@api.route('/init/')
class Job(Resource):
    @api.expect(init_query_model)
    def post(self):
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        config_obj["server"] = os.environ["SERVER"]
        res_obj = {}
        try:
            req_obj = request.json
            trim_object(req_obj)
            res_obj = job_init(config_obj, os.environ["DATA_PATH"])
        except Exception as e:
            res_obj = log_error(traceback.format_exc())
        http_code = 500 if "error_list" in res_obj else 200
        return res_obj, http_code

    @api.doc(False)
    def get(self):
        return self.post()


@api.route('/addnew/')
class Job(Resource):
    @api.expect(addnew_query_model)
    def post(self):
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        config_obj["server"] = os.environ["SERVER"]
        res_obj = {}
        try:
            req_obj = request.json
            trim_object(req_obj)
            data_path, server = os.environ["DATA_PATH"],os.environ["SERVER"]
            res_obj = job_addnew(req_obj, config_obj, data_path, server)
        except Exception as e:
            res_obj = log_error(traceback.format_exc())
        
        http_code = 500 if "error_list" in res_obj else 200
        return res_obj, http_code
    
    @api.doc(False)
    def get(self):
        return self.post()

@api.route('/detail/')
class Job(Resource):
    @api.expect(detail_query_model)
    def post(self):
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        config_obj["server"] = os.environ["SERVER"]
        res_obj = {}
        try:
            req_obj = request.json
            trim_object(req_obj)
            res_obj = job_detail(req_obj, config_obj)
        except Exception as e:
            res_obj = log_error(traceback.format_exc())
        http_code = 500 if "error_list" in res_obj else 200
        return res_obj, http_code

    @api.doc(False)
    def get(self):
        return self.post()

@api.route('/list/')
class Job(Resource):
    @api.expect(list_query_model)
    def post(self):
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        config_obj["server"] = os.environ["SERVER"]
        res_obj = {}
        try:
            req_obj = request.json
            trim_object(req_obj)
            res_obj = job_list(req_obj, config_obj)
        except Exception as e:
            res_obj = log_error(traceback.format_exc())
        
        http_code = 500 if "error_list" in res_obj else 200
        return res_obj, http_code
        
    @api.doc(False)
    def get(self):
        return self.post()

@api.route('/update/')
class Job(Resource):
    @api.doc(False)
    @api.expect(update_query_model)
    def post(self):
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        config_obj["server"] = os.environ["SERVER"]
        res_obj = {}
        try:
            req_obj = request.json
            trim_object(req_obj)
            res_obj = job_update(req_obj, config_obj)
        except Exception as e:
            res_obj = log_error(traceback.format_exc())
        http_code = 500 if "error_list" in res_obj else 200
        return res_obj, http_code

    @api.doc(False)
    def get(self):
        return self.post()


@api.route('/delete/')
class Job(Resource):
    @api.expect(delete_query_model)
    def post(self):
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        config_obj["server"] = os.environ["SERVER"]
        res_obj = {}
        try:
            req_obj = request.json
            trim_object(req_obj)
            res_obj = job_delete(req_obj, config_obj)
        except Exception as e:
            res_obj = log_error(traceback.format_exc())
        http_code = 500 if "error_list" in res_obj else 200
        return res_obj, http_code

    @api.doc(False)
    def get(self):
        return self.post()


@api.route('/results/')
class Job(Resource):
    @api.expect(results_query_model)
    def post(self):
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        config_obj["server"] = os.environ["SERVER"]
        res_obj = {}
        try:
            req_obj = request.json
            trim_object(req_obj)
            res_obj = job_results(req_obj, config_obj)
        except Exception as e:
            res_obj = log_error(traceback.format_exc())
        
        http_code = 500 if "error_list" in res_obj else 200
        return res_obj, http_code

    @api.doc(False)
    def get(self):
        return self.post()

@api.route('/status/')
class Job(Resource):
    @api.expect(status_query_model)
    def post(self):
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        config_obj["server"] = os.environ["SERVER"]
        res_obj = {}
        try:
            req_obj = request.json
            trim_object(req_obj)
            res_obj = job_status(req_obj, config_obj)
        except Exception as e:
            res_obj = log_error(traceback.format_exc())
        
        http_code = 500 if "error_list" in res_obj else 200
        return res_obj, http_code

    @api.doc(False)
    def get(self):
        return self.post()


@api.route('/queue/')
class Job(Resource):
    @api.expect(queue_query_model)
    def post(self):
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        config_obj["server"] = os.environ["SERVER"]
        res_obj = {}
        try:
            req_obj = request.json
            trim_object(req_obj)
            res_obj = job_queue(req_obj, config_obj)
        except Exception as e:
            res_obj = log_error(traceback.format_exc())
        
        http_code = 500 if "error_list" in res_obj else 200
        return res_obj, http_code

    @api.doc(False)
    def get(self):
        return self.post()


@api.route('/clean/')
class Job(Resource):
    @api.doc(False)
    @api.expect(clean_query_model)
    def post(self):
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        config_obj["server"] = os.environ["SERVER"]
        res_obj = {}
        try:
            data_path, server = os.environ["DATA_PATH"],os.environ["SERVER"]
            res_obj = job_clean(data_path, server)
        except Exception as e:
            res_obj = log_error(traceback.format_exc())
        
        http_code = 500 if "error_list" in res_obj else 200
        return res_obj, http_code

    @api.doc(False)
    def get(self):
        return self.post()


