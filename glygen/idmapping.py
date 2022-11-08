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
from flask_jwt_extended import (
    jwt_required, get_jwt_identity
)

from glygen.idmapping_apilib import search_init, search
from glygen.util import get_error_obj, trim_object, get_cached_records_direct
import traceback


api = Namespace("idmapping", description="IDmapping APIs")

search_init_query_model = api.model(
    'Search Init Query', 
    { 'query': fields.String(required=True, default="", description='')}
)

search_query_model = api.model(
    'Search Query',
    { 'query': fields.String(required=True, default="", description='')}
)

list_query_model = api.model(
    'List Query',
    { 'query': fields.String(required=True, default="", description='')}
)



@api.route('/search_init/')
class Idmapping(Resource):
    @api.doc('search_init')
    @api.expect(search_init_query_model)
    def post(self):
        api_name = "idmapping_search_init"
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        res_obj = {}
        try:
            req_obj = request.json
            trim_object(req_obj)
            data_path = current_app.config["DATA_PATH"]
            res_obj = search_init(config_obj)
        except Exception as e:
            log_path = current_app.config["LOG_PATH"] 
            res_obj = get_error_obj(api_name, traceback.format_exc(), log_path)
        return res_obj



@api.route('/search/')
class Idmapping(Resource):
    @api.doc('search')
    @api.expect(search_query_model)
    def post(self):
        api_name = "idmapping_search"
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        res_obj = {}
        try:
            req_obj = request.json
            trim_object(req_obj)
            res_obj = search(req_obj, config_obj)
        except Exception as e:
            log_path = current_app.config["LOG_PATH"]
            res_obj = get_error_obj(api_name, traceback.format_exc(), log_path)
        return res_obj


@api.route('/list/')
class Idmapping(Resource):
    @api.doc('list')
    @api.expect(list_query_model)
    def post(self):
        api_name = "idmapping_list"
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        res_obj = {}
        try:
            req_obj = request.json
            trim_object(req_obj)
            res_obj = get_cached_records_direct(req_obj, config_obj)
        except Exception as e:
            log_path = current_app.config["LOG_PATH"]
            res_obj = get_error_obj(api_name, traceback.format_exc(), log_path)
        return res_obj






