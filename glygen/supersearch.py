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

from glygen.supersearch_apilib import search_init, search
from glygen.util import trim_object, get_cached_records_indirect
import traceback


api = Namespace("supersearch", description="Supersearch APIs")


search_init_query_model = api.model("Supersearch Init Query", {})
list_query_model = api.model("Supersearch List Query",{ "id": fields.String(required=True, default="")})

UNAGGREGATED = api.model(
    "UNAGGREGATED",
    {
        "order":fields.Integer(required=True, default=1), 
        "path":fields.String(required=True, default="uniprot_ac"),
        "operator":fields.String(required=True, default="$eq"),
        "string_value":fields.String(required=True, default="P14210")
    }
)


QUERY = api.model(
    "QUERY",
    {
        "aggregator": fields.String(required=True, default="$and"),
        "unaggregated_list": fields.List(fields.Nested(UNAGGREGATED), required=True),
        "aggregated_list":fields.List(fields.String(), required=True, default=[])
    }
)

CONCEPT_QUERY = api.model(
    "CONCEPT_QUERY", 
    {
        "concept": fields.String(required=True, default="protein"),
        "query":fields.Nested(QUERY)
    }
)

search_query_model = api.model(
    'Supersearch Query', 
    { 
        "concept_query_list": fields.List(fields.Nested(CONCEPT_QUERY), required=True)
    }
)




@api.route('/search_init/')
class Supersearch(Resource):
    @api.expect(search_init_query_model)
    def post(self):
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        
        json_url = os.path.join(SITE_ROOT, "conf/supersearch.json")
        supersearch_config_obj = json.load(open(json_url))
        config_obj["ignored_path_list"] = supersearch_config_obj["ignored_path_list"]
        config_obj["path_map"] = supersearch_config_obj["path_map"]
        json_url = os.path.join(SITE_ROOT, "conf/edgerules.json")
        config_obj["ignored_edges"] = json.load(open(json_url))

        res_obj = {}
        try:
            res_obj = search_init(config_obj)
        except Exception as e:
            res_obj = log_error(traceback.format_exc())
        return res_obj

    @api.doc(False)
    def get(self):
        return self.post()


@api.route('/search/')
class Supersearch(Resource):
    @api.expect(search_query_model)
    def post(self):
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        
        json_url = os.path.join(SITE_ROOT, "conf/supersearch.json")
        supersearch_config_obj = json.load(open(json_url))
        config_obj["ignored_path_list"] = supersearch_config_obj["ignored_path_list"]
        config_obj["path_map"] = supersearch_config_obj["path_map"]
        json_url = os.path.join(SITE_ROOT, "conf/edgerules.json")
        config_obj["ignored_edges"] = json.load(open(json_url))

        res_obj = {}
        try:
            req_obj = request.json
            trim_object(req_obj)
            res_obj = search(req_obj, config_obj, False, False)
        except Exception as e:
            res_obj = log_error(traceback.format_exc())
        return res_obj

    @api.doc(False)
    def get(self):
        return self.post()

@api.route('/reason/')
class Supersearch(Resource):
    @api.doc(False)
    def post(self):
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        json_url = os.path.join(SITE_ROOT, "conf/supersearch.json")
        supersearch_config_obj = json.load(open(json_url))
        config_obj["ignored_path_list"] = supersearch_config_obj["ignored_path_list"]
        config_obj["path_map"] = supersearch_config_obj["path_map"]
        json_url = os.path.join(SITE_ROOT, "conf/edgerules.json")
        config_obj["ignored_edges"] = json.load(open(json_url))

        res_obj = {}
        try:
            req_obj = request.json
            trim_object(req_obj)
            res_obj = search(req_obj, config_obj, True, False)
        except Exception as e:
            res_obj = log_error(traceback.format_exc())
        return res_obj

    @api.doc(False)
    def get(self):
        return self.post()


@api.route('/list/')
class Supersearch(Resource):
    @api.expect(list_query_model)
    def post(self):
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        json_url = os.path.join(SITE_ROOT, "conf/supersearch.json")
        supersearch_config_obj = json.load(open(json_url))
        config_obj["ignored_path_list"] = supersearch_config_obj["ignored_path_list"]
        config_obj["path_map"] = supersearch_config_obj["path_map"]
        json_url = os.path.join(SITE_ROOT, "conf/edgerules.json")
        config_obj["ignored_edges"] = json.load(open(json_url))

        res_obj = {}
        try:
            req_obj = request.json
            trim_object(req_obj)
            res_obj = get_cached_records_indirect(req_obj, config_obj)
        except Exception as e:
            res_obj = log_error(traceback.format_exc())
        return res_obj

    @api.doc(False)
    def get(self):
        return self.post()





