import os,sys
from flask_restx import Namespace, Resource, fields
from flask import (request, current_app)
from glygen.document import get_one, get_many, insert_one, update_one, delete_one, order_json_obj
from werkzeug.utils import secure_filename
import datetime
import time
import subprocess
import json
import bcrypt
from flask_jwt_extended import (
    jwt_required, get_jwt_identity
)

from glygen.xxx_apilib import xxx_yyy, xxx_yyy, xxx_yyy, xxx_yyy, xxx_yyy, xxx_yyy, xxx_yyy, xxx_yyy
from glygen.util import xxx_yyy, get_error_obj, trim_object
import traceback


api = Namespace("xxx", description="Xxx APIs")
yyy_query_model = api.model('Yyy Query',{ 'query':fields.String(required=True, default="", description="")})
yyy_query_model = api.model('Yyy Query',{ 'query':fields.String(required=True, default="", description="")})
yyy_query_model = api.model('Yyy Query',{ 'query':fields.String(required=True, default="", description="")})
yyy_query_model = api.model('Yyy Query',{ 'query':fields.String(required=True, default="", description="")})
yyy_query_model = api.model('Yyy Query',{ 'query':fields.String(required=True, default="", description="")})
yyy_query_model = api.model('Yyy Query',{ 'query':fields.String(required=True, default="", description="")})
yyy_query_model = api.model('Yyy Query',{ 'query':fields.String(required=True, default="", description="")})
yyy_query_model = api.model('Yyy Query',{ 'query':fields.String(required=True, default="", description="")})




@api.route('/yyy/')
class Xxx(Resource):
    @api.doc('yyy')
    @api.expect(xxx_query_model)
    def post(self):
        api_name = "xxx_yyy"
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        res_obj = {}
        try:
            req_obj = request.json
            trim_object(req_obj)
            res_obj = xxx_yyy(req_obj, config_obj)
        except Exception as e:
            log_path = current_app.config["LOG_PATH"]
            res_obj = get_error_obj(api_name, traceback.format_exc(), log_path)
        http_code = 500 if "error_list" in res_obj else 200
        return res_obj


@api.route('/yyy/')
class Xxx(Resource):
    @api.doc('yyy')
    @api.expect(xxx_query_model)
    def post(self):
        api_name = "xxx_yyy"
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        res_obj = {}
        try:
            req_obj = request.json
            trim_object(req_obj)
            res_obj = xxx_yyy(req_obj, config_obj)
        except Exception as e:
            log_path = current_app.config["LOG_PATH"]
            res_obj = get_error_obj(api_name, traceback.format_exc(), log_path)
        http_code = 500 if "error_list" in res_obj else 200
        return res_obj


@api.route('/yyy/')
class Xxx(Resource):
    @api.doc('yyy')
    @api.expect(xxx_query_model)
    def post(self):
        api_name = "xxx_yyy"
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        res_obj = {}
        try:
            req_obj = request.json
            trim_object(req_obj)
            res_obj = xxx_yyy(req_obj, config_obj)
        except Exception as e:
            log_path = current_app.config["LOG_PATH"]
            res_obj = get_error_obj(api_name, traceback.format_exc(), log_path)
        http_code = 500 if "error_list" in res_obj else 200
        return res_obj


@api.route('/yyy/')
class Xxx(Resource):
    @api.doc('yyy')
    @api.expect(xxx_query_model)
    def post(self):
        api_name = "xxx_yyy"
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        res_obj = {}
        try:
            req_obj = request.json
            trim_object(req_obj)
            res_obj = xxx_yyy(req_obj, config_obj)
        except Exception as e:
            log_path = current_app.config["LOG_PATH"]
            res_obj = get_error_obj(api_name, traceback.format_exc(), log_path)
        http_code = 500 if "error_list" in res_obj else 200
        return res_obj


@api.route('/yyy/')
class Xxx(Resource):
    @api.doc('yyy')
    @api.expect(xxx_query_model)
    def post(self):
        api_name = "xxx_yyy"
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        res_obj = {}
        try:
            req_obj = request.json
            trim_object(req_obj)
            res_obj = xxx_yyy(req_obj, config_obj)
        except Exception as e:
            log_path = current_app.config["LOG_PATH"]
            res_obj = get_error_obj(api_name, traceback.format_exc(), log_path)
        http_code = 500 if "error_list" in res_obj else 200
        return res_obj


@api.route('/yyy/')
class Xxx(Resource):
    @api.doc('yyy')
    @api.expect(xxx_query_model)
    def post(self):
        api_name = "xxx_yyy"
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        res_obj = {}
        try:
            req_obj = request.json
            trim_object(req_obj)
            res_obj = xxx_yyy(req_obj, config_obj)
        except Exception as e:
            log_path = current_app.config["LOG_PATH"]
            res_obj = get_error_obj(api_name, traceback.format_exc(), log_path)
        http_code = 500 if "error_list" in res_obj else 200
        return res_obj


@api.route('/yyy/')
class Xxx(Resource):
    @api.doc('yyy')
    @api.expect(xxx_query_model)
    def post(self):
        api_name = "xxx_yyy"
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        res_obj = {}
        try:
            req_obj = request.json
            trim_object(req_obj)
            res_obj = xxx_yyy(req_obj, config_obj)
        except Exception as e:
            log_path = current_app.config["LOG_PATH"]
            res_obj = get_error_obj(api_name, traceback.format_exc(), log_path)
        http_code = 500 if "error_list" in res_obj else 200
        return res_obj


@api.route('/yyy/')
class Xxx(Resource):
    @api.doc('yyy')
    @api.expect(xxx_query_model)
    def post(self):
        api_name = "xxx_yyy"
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        res_obj = {}
        try:
            req_obj = request.json
            trim_object(req_obj)
            res_obj = xxx_yyy(req_obj, config_obj)
        except Exception as e:
            log_path = current_app.config["LOG_PATH"]
            res_obj = get_error_obj(api_name, traceback.format_exc(), log_path)
        http_code = 500 if "error_list" in res_obj else 200
        return res_obj


@api.route('/yyy/')
class Xxx(Resource):
    @api.doc('yyy')
    @api.expect(xxx_query_model)
    def post(self):
        api_name = "xxx_yyy"
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        res_obj = {}
        try:
            req_obj = request.json
            trim_object(req_obj)
            res_obj = xxx_yyy(req_obj, config_obj)
        except Exception as e:
            log_path = current_app.config["LOG_PATH"]
            res_obj = get_error_obj(api_name, traceback.format_exc(), log_path)
        http_code = 500 if "error_list" in res_obj else 200
        return res_obj


@api.route('/yyy/')
class Xxx(Resource):
    @api.doc('yyy')
    @api.expect(xxx_query_model)
    def post(self):
        api_name = "xxx_yyy"
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        res_obj = {}
        try:
            req_obj = request.json
            trim_object(req_obj)
            res_obj = xxx_yyy(req_obj, config_obj)
        except Exception as e:
            log_path = current_app.config["LOG_PATH"]
            res_obj = get_error_obj(api_name, traceback.format_exc(), log_path)
        http_code = 500 if "error_list" in res_obj else 200
        return res_obj


@api.route('/yyy/')
class Xxx(Resource):
    @api.doc('yyy')
    @api.expect(xxx_query_model)
    def post(self):
        api_name = "xxx_yyy"
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        res_obj = {}
        try:
            req_obj = request.json
            trim_object(req_obj)
            res_obj = xxx_yyy(req_obj, config_obj)
        except Exception as e:
            log_path = current_app.config["LOG_PATH"]
            res_obj = get_error_obj(api_name, traceback.format_exc(), log_path)
        http_code = 500 if "error_list" in res_obj else 200
        return res_obj






