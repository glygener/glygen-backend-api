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

from glygen.protein_apilib import protein_search_init, protein_search, protein_search_simple, protein_detail, protein_alignment
from glygen.util import get_cached_records_indirect, get_error_obj, trim_object
import traceback


api = Namespace("protein", description="Protein APIs")
search_init_query_model = api.model(
    'Search Init Query',
    { 'query': fields.String(required=True, default="", description='')}
)
search_simple_query_model = api.model(
    'Simple Search Query',
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


alignment_query_model = api.model(
    'Alignment Query',
    { 'query': fields.String(required=True, default="", description='')}
) 


@api.route('/search_init/')
class Protein(Resource):
    @api.doc('search_init')
    @api.expect(search_query_model)
    def post(self):
        api_name = "protein_search_init"
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        res_obj = {}
        try:
            req_obj = request.json
            trim_object(req_obj)
            res_obj = protein_search_init(config_obj)
        except Exception as e:
            log_path = current_app.config["LOG_PATH"] 
            res_obj = get_error_obj(api_name, traceback.format_exc(), log_path)
        http_code = 500 if "error_list" in res_obj else 200 
        return res_obj

    def get(self):
        return self.post()

@api.route('/search/')
class Protein(Resource):
    @api.doc('search')
    @api.expect(search_query_model)
    def post(self):
        api_name = "protein_search"
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        res_obj = {}
        try:
            req_obj = request.json
            trim_object(req_obj)
            res_obj = protein_search(req_obj, config_obj)
        except Exception as e:
            log_path = current_app.config["LOG_PATH"] 
            res_obj = get_error_obj(api_name, traceback.format_exc(), log_path)
        http_code = 500 if "error_list" in res_obj else 200 
        return res_obj
    
    def get(self):
        return self.post()


@api.route('/search_simple/')
class Protein(Resource):
    @api.doc('search_simple')
    @api.expect(search_simple_query_model)
    def post(self):
        api_name = "protein_search_simple"
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        res_obj = {}
        try:
            req_obj = request.json
            trim_object(req_obj)
            res_obj = protein_search_simple(req_obj, config_obj)
        except Exception as e:
            log_path = current_app.config["LOG_PATH"]
            res_obj = get_error_obj(api_name, traceback.format_exc(), log_path)
        http_code = 500 if "error_list" in res_obj else 200
        return res_obj

    def get(self):
        return self.post()


@api.route('/list/')
class Protein(Resource):
    @api.doc('list')
    @api.expect(list_query_model)
    def post(self):
        api_name = "protein_list"
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        res_obj = {}
        try:
            req_obj = request.json
            trim_object(req_obj)
            res_obj = get_cached_records_indirect(req_obj, config_obj)
        except Exception as e:
            log_path = current_app.config["LOG_PATH"]
            res_obj = get_error_obj(api_name, traceback.format_exc(), log_path)
        http_code = 500 if "error_list" in res_obj else 200
        return res_obj

    def get(self):
        return self.post()



@api.route('/detail/<uniprot_canonical_ac>/')
class Protein(Resource):
    @api.doc('detail')
    def post(self, uniprot_canonical_ac):
        api_name = "protein_detail"
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        res_obj = {}
        try:
            req_obj = {"uniprot_canonical_ac":uniprot_canonical_ac}
            res_obj = protein_detail(req_obj, config_obj)
        except Exception as e:
            log_path = current_app.config["LOG_PATH"]
            res_obj = get_error_obj(api_name, traceback.format_exc(), log_path)
        http_code = 500 if "error_list" in res_obj else 200
        return res_obj

    def get(self, uniprot_canonical_ac):
        return self.post(uniprot_canonical_ac)


@api.route('/alignment/')
class Protein(Resource):
    @api.doc('alignment')
    @api.expect(alignment_query_model)
    def post(self):
        api_name = "protein_alignment"
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        res_obj = {}
        try:
            req_obj = request.json
            trim_object(req_obj)
            res_obj = protein_alignment(req_obj, config_obj)
        except Exception as e:
            log_path = current_app.config["LOG_PATH"]
            res_obj = get_error_obj(api_name, traceback.format_exc(), log_path)
        http_code = 500 if "error_list" in res_obj else 200
        return res_obj

    def get(self):
        return self.post()





