import os,sys
from flask_restx import Namespace, Resource, fields
from flask import (request, current_app)
from glygen.db import log_error
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
from glygen.util import get_cached_records_indirect, trim_object
import traceback


api = Namespace("protein", description="Protein APIs")

search_init_query_model = api.model("Protein Search Init Query", {})
search_simple_query_model = api.model("Protein Simple Search Query", 
    {
        "term_category": fields.String(required=True, default="P12314"),
        "term": fields.String(required=True, default="protein")
    }
)
search_query_model = api.model("Protein Search Query",
    { "uniprot_canonical_ac": fields.String(required=True, default="P12314")}
)
list_query_model = api.model("Protein List Query",{ "id": fields.String(required=True, default="")})

alignment_query_model = api.model("Protein Alignment Query",
    { 
        "uniprot_canonical_ac": fields.String(required=True, default="P14210-1"),
        "cluster_type": fields.String(required=True, default="homologset.oma")
    }
) 




@api.route('/search_init/')
class Protein(Resource):
    @api.doc('search_init')
    @api.expect(search_init_query_model)
    def post(self):
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        res_obj = {}
        try:
            res_obj = protein_search_init(config_obj)
        except Exception as e:
            res_obj = log_error(traceback.format_exc())
        http_code = 500 if "error_list" in res_obj else 200 
        return res_obj

    @api.doc(False)
    def get(self):
        return self.post()

@api.route('/search/')
class Protein(Resource):
    @api.doc('search')
    @api.expect(search_query_model)
    def post(self):
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        res_obj = {}
        try:
            req_obj = request.json
            trim_object(req_obj)
            res_obj = protein_search(req_obj, config_obj)
        except Exception as e:
            res_obj = log_error(traceback.format_exc())
        http_code = 500 if "error_list" in res_obj else 200 
        return res_obj
    
    @api.doc(False)
    def get(self):
        return self.post()


@api.route('/search_simple/')
class Protein(Resource):
    @api.doc('search_simple')
    @api.expect(search_simple_query_model)
    def post(self):
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        res_obj = {}
        try:
            req_obj = request.json
            trim_object(req_obj)
            res_obj = protein_search_simple(req_obj, config_obj)
        except Exception as e:
            res_obj = log_error(traceback.format_exc())
        http_code = 500 if "error_list" in res_obj else 200
        return res_obj

    @api.doc(False)
    def get(self):
        return self.post()


@api.route('/list/')
class Protein(Resource):
    @api.doc('list')
    @api.expect(list_query_model)
    def post(self):
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        res_obj = {}
        try:
            req_obj = request.json
            trim_object(req_obj)
            res_obj = get_cached_records_indirect(req_obj, config_obj)
        except Exception as e:
            res_obj = log_error(traceback.format_exc())
        http_code = 500 if "error_list" in res_obj else 200
        return res_obj

    @api.doc(False)
    def get(self):
        return self.post()



@api.route('/detail/<uniprot_canonical_ac>/')
@api.doc(params={"uniprot_canonical_ac": {"in": "query", "default": "P14210"}})
class Protein(Resource):
    @api.doc('detail')
    def post(self, uniprot_canonical_ac):
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        res_obj = {}
        try:
            req_obj = {"uniprot_canonical_ac":uniprot_canonical_ac}
            res_obj = protein_detail(req_obj, config_obj)
        except Exception as e:
            res_obj = log_error(traceback.format_exc())
        http_code = 500 if "error_list" in res_obj else 200
        return res_obj

    @api.doc(False)
    def get(self, uniprot_canonical_ac):
        return self.post(uniprot_canonical_ac)


@api.route('/alignment/')
class Protein(Resource):
    @api.doc('alignment')
    @api.expect(alignment_query_model)
    def post(self):
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        res_obj = {}
        try:
            req_obj = request.json
            trim_object(req_obj)
            res_obj = protein_alignment(req_obj, config_obj)
        except Exception as e:
            res_obj = log_error(traceback.format_exc())
        http_code = 500 if "error_list" in res_obj else 200
        return res_obj

    @api.doc(False)
    def get(self):
        return self.post()





