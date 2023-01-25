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

from glygen.log_apilib import log_logging, log_init, log_access, log_grouped
from glygen.util import trim_object
import traceback


api = Namespace("log", description="Log APIs")

init_query_model = api.model(
    'Log Init Query', 
    { 
        "start_date": fields.String(required=True, default="2022-1-1 1:1:1 EDT-0400"),
        "end_date": fields.String(required=True, default="2022-12-31 1:1:1 EDT-0400")
    }
)

logging_query_model = api.model(
    'Log Logging Query', 
    {
        "type":fields.String(required=True, default="error"),
        "page":fields.String(required=True, default="index.html"),
        "user":fields.String(required=True, default="some_username"),
        "id":fields.String(required=True, default=""),
        "message":fields.String(required=True, default="")
    }
)

access_query_model = api.model(
    'Log Access Query', 
    { 
        "start_date": fields.String(required=True, default="2022-1-1 1:1:1 EDT-0400"),
        "end_date": fields.String(required=True, default="2022-12-31 1:1:1 EDT-0400"),
        "type":fields.String(required=True, default="error"),
        "page":fields.String(required=True, default="index.html"),
        "user":fields.String(required=True, default="some_username"),
        "order":fields.String(required=True, default="asc"),
        "offset":fields.Integer(required=True, default=1),
        "limit":fields.Integer(required=True, default=100)
    }
)

grouped_query_model = api.model(
    'Log Grouped Query', 
    { 
        "start_date": fields.String(required=True, default="2022-1-1 1:1:1 EDT-0400"),
        "end_date": fields.String(required=True, default="2022-12-31 1:1:1 EDT-0400"),
        "type":fields.String(required=True, default="error"),
        "page":fields.String(required=True, default="index.html"),
        "user":fields.String(required=True, default="some_username"),
        "order":fields.String(required=True, default="asc"),
        "offset":fields.Integer(required=True, default=1),
        "limit":fields.Integer(required=True, default=100)
    }
)



@api.route('/logging/')
class Log(Resource):
    @api.doc('logging')
    @api.expect(logging_query_model)
    def post(self):
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        res_obj = {}
        try:
            req_obj = request.json
            trim_object(req_obj)
            data_path = os.environ["DATA_PATH"]
            res_obj = log_logging(req_obj, config_obj)
        except Exception as e:
            res_obj = log_error(traceback.format_exc())
        
        http_code = 500 if "error_list" in res_obj else 200
        return res_obj, http_code

    @api.doc(False)
    def get(self):
        return self.post()


@api.route('/init/')
class Log(Resource):
    @api.doc('init')
    @api.expect(init_query_model)
    def post(self):
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        res_obj = {}
        try:
            req_obj = request.json
            trim_object(req_obj)
            data_path = os.environ["DATA_PATH"]
            res_obj = log_init(req_obj, config_obj)
        except Exception as e:
            res_obj = log_error(traceback.format_exc())
        
        http_code = 500 if "error_list" in res_obj else 200
        return res_obj, http_code

    @api.doc(False)
    def get(self):
        return self.post()

@api.route('/access/')
class Log(Resource):
    @api.doc('access')
    @api.expect(access_query_model)
    def post(self):
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        res_obj = {}
        try:
            req_obj = request.json
            trim_object(req_obj)
            data_path = os.environ["DATA_PATH"]
            res_obj = log_access(req_obj, config_obj)
        except Exception as e:
            res_obj = log_error(traceback.format_exc())
        
        http_code = 500 if "error_list" in res_obj else 200
        return res_obj, http_code

    @api.doc(False)
    def get(self):
        return self.post()


@api.route('/grouped/')
class Log(Resource):
    @api.doc('grouped')
    @api.expect(grouped_query_model)
    def post(self):
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        res_obj = {}
        try:
            req_obj = request.json
            trim_object(req_obj)
            data_path = os.environ["DATA_PATH"]
            res_obj = log_grouped(req_obj, config_obj)
        except Exception as e:
            res_obj = log_error(traceback.format_exc())
        
        http_code = 500 if "error_list" in res_obj else 200
        return res_obj, http_code


    @api.doc(False)
    def get(self):
        return self.post()




