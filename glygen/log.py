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

logging_query_model = api.model(
    'Logging Query', { 'query': fields.String(required=True, default="", description='')})
init_query_model = api.model(
    'Init Query', { 'query': fields.String(required=True, default="", description='')})
access_query_model = api.model(
    'Access Query', { 'query': fields.String(required=True, default="", description='')})
grouped_query_model = api.model(
    'Grouped Query', { 'query': fields.String(required=True, default="", description='')})



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
        return res_obj

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
        
        return res_obj

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
        
        return res_obj

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
        
        return res_obj


    @api.doc(False)
    def get(self):
        return self.post()




