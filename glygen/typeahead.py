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

from glygen.typeahead_apilib import glycan_typeahead, protein_typeahead, global_typeahead, categorized_typeahead
from glygen.util import get_error_obj, trim_object, get_cached_records_direct
import traceback



api = Namespace("typeahead", description="IDmapping APIs")

typeahead_query_model = api.model(
    'Search Init Query', 
    { 'query': fields.String(required=True, default="", description='')}
)

categorized_typeahead_query_model = api.model(
    'Categorized Typeahead Query',
    { 'query': fields.String(required=True, default="", description='')}
)

global_typeahead_query_model = api.model(
    'Global Typeahead Query',
    { 'query': fields.String(required=True, default="", description='')}
)



@api.route('/typeahead/')
class Typeahead(Resource):
    @api.doc('typeahead')
    @api.expect(typeahead_query_model)
    def post(self):
        api_name = "typeahead_typeahead"
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        res_obj = {}
        try:
            req_obj = request.json
            trim_object(req_obj)
            data_path = os.environ["DATA_PATH"]
            field_list_one = ["glytoucan_ac", "motif_name", "enzyme_uniprot_canonical_ac", 
                    "glycan_pmid", "enzyme"]
            field_list_two = ["uniprot_canonical_ac", "uniprot_id", "refseq_ac", 
                                "protein_name", "gene_name", "pathway_id", "pathway_name", 
                                "disease_name","disease_id", 
                                "go_id", "go_term", "protein_pmid"] 
            tmp_obj_one, tmp_obj_two = [], []
            if req_obj["field"] in field_list_one:
                tmp_obj_one = glycan_typeahead(req_obj, config_obj)
            if req_obj["field"] in field_list_two:
                tmp_obj_two = protein_typeahead(req_obj, config_obj)
            if "error_list" in tmp_obj_one:
                res_obj = tmp_obj_one
            elif "error_list" in tmp_obj_two: 
                res_obj = tmp_obj_two
            else:
                res_obj = tmp_obj_one + tmp_obj_two

        except Exception as e:
            log_path = current_app.config["LOG_PATH"] 
            res_obj = get_error_obj(api_name, traceback.format_exc(), log_path)
        return res_obj


    @api.doc(False)
    def get(self):
        return self.post()



@api.route('/categorized_typeahead/')
class Typeahead(Resource):
    @api.doc('categorized_typeahead')
    @api.expect(categorized_typeahead_query_model)
    def post(self):
        api_name = "categorized_typeahead"
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        res_obj = {}
        try:
            req_obj = request.json
            trim_object(req_obj)
            tmp_obj = categorized_typeahead(req_obj, config_obj)
            if "error_list" in tmp_obj:
                res_obj = tmp_obj
            else:
                res_obj = tmp_obj
        except Exception as e:
            log_path = current_app.config["LOG_PATH"]
            res_obj = get_error_obj(api_name, traceback.format_exc(), log_path)
        return res_obj

    @api.doc(False)
    def get(self):
        return self.post()

@api.route('/global_typeahead/')
class Typeahead(Resource):
    @api.doc('global_typeahead')
    @api.expect(global_typeahead_query_model)
    def post(self):
        api_name = "global_typeahead"
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        res_obj = {}
        try:
            req_obj = request.json
            trim_object(req_obj)
            tmp_obj = global_typeahead(req_obj, config_obj)
            if "error_list" in tmp_obj:
                res_obj = tmp_obj
            else:
                res_obj = tmp_obj
        except Exception as e:
            log_path = current_app.config["LOG_PATH"]
            res_obj = get_error_obj(api_name, traceback.format_exc(), log_path)
        return res_obj


    @api.doc(False)
    def get(self):
        return self.post()




