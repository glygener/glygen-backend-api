import os,sys
from flask_restx import Namespace, Resource, fields
from flask import (request, current_app)
from glygen.db import log_error, log_request
from glygen.document import get_one, get_many, insert_one, update_one, delete_one, order_json_obj
from werkzeug.utils import secure_filename
import datetime
import time
import subprocess
import json
import bcrypt

from glygen.mcp_apilib import site_search, variant_search, map_variants, get_cached
from glygen.util import trim_object, get_req_obj
import traceback


api = Namespace("mcp", description="MCP APIs")

site_search_query_model = api.model(
    "Site Search Query",
    {
        "tax_id": fields.String(required=True, default=9606),
        "tissue_id": fields.String(required=True, default="UBERON:0002107")
    }
)
variant_search_query_model = api.model(
    "Variant Search Query",
    {
        "tax_id": fields.String(required=True, default=9606),
        "tissue_id": fields.String(required=True, default="UBERON:0002107")
    }
)
map_variants_query_model = api.model(
    "Map Variants Query",
    {
        "site_result_id": fields.String(required=True, default=""),
        "variant_result_id": fields.String(required=True, default="")
    }
)



@api.route('/site_search/')
class Site(Resource):
    @api.expect(site_search_query_model)
    def post(self):
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        res_obj, log_obj = {}, {}
        try:
            req_obj = get_req_obj(request)
            log_obj = log_request({}, "/mcp/mcp_site_search/", request)
            if "error_list" not in log_obj:
                res_obj = site_search(req_obj, config_obj)
        except Exception as e:
            res_obj = log_error(traceback.format_exc(), log_obj)
        http_code = 500 if "error_list" in res_obj else 200
        return res_obj, http_code

    @api.doc(False)
    def get(self):
        return self.post()


@api.route('/variant_search/')
class Site(Resource):
    @api.expect(variant_search_query_model)
    def post(self):
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        res_obj, log_obj = {}, {}
        try:
            req_obj = get_req_obj(request)
            log_obj = log_request({}, "/mcp/mcp_variant_search/", request)
            if "error_list" not in log_obj:
                res_obj = variant_search(req_obj, config_obj)
        except Exception as e:
            res_obj = log_error(traceback.format_exc(), log_obj)
        http_code = 500 if "error_list" in res_obj else 200
        return res_obj, http_code

    @api.doc(False)
    def get(self):
        return self.post()


@api.route('/map_variants/')
class Site(Resource):
    @api.expect(map_variants_query_model)
    def post(self):
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        res_obj, log_obj = {}, {}
        try:
            req_obj = get_req_obj(request)
            log_obj = log_request({}, "/mcp/mcp_map_variants/", request)
            if "error_list" not in log_obj:
                res_obj = map_variants(req_obj, config_obj)
        except Exception as e:
            res_obj = log_error(traceback.format_exc(), log_obj)
        http_code = 500 if "error_list" in res_obj else 200
        return res_obj, http_code

    @api.doc(False)
    def get(self):
        return self.post()

@api.route('/get_cached/')
class Site(Resource):
    @api.expect(map_variants_query_model)
    def post(self):
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        res_obj, log_obj = {}, {}
        try:
            req_obj = get_req_obj(request)
            log_obj = log_request({}, "/mcp/mcp_get_cached/", request)
            if "error_list" not in log_obj:
                res_obj = get_cached(req_obj, config_obj)
        except Exception as e:
            res_obj = log_error(traceback.format_exc(), log_obj)
        http_code = 500 if "error_list" in res_obj else 200
        return res_obj, http_code

    @api.doc(False)
    def get(self):
        return self.post()






