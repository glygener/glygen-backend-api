import os,sys
from flask_restx import Namespace, Resource, fields
from flask import (request, current_app, send_file)
from glygen.db import log_error, log_request
from glygen.document import get_one, get_many, insert_one, update_one, delete_one, order_json_obj
from werkzeug.utils import secure_filename
import datetime
import time
import subprocess
import json
import bcrypt

from glygen.biomarker_apilib import biomarker_detail, biomarker_search, biomarker_search_init, biomarker_search_simple
from glygen.util import get_req_obj, get_cached_records_indirect, get_hash_id, cache_result_list, get_cached_result_list, apply_pagination
import traceback



api = Namespace("biomarker", description="Biomarker APIs")


search_init_query_model = api.model("Biomarker Search Init Query", {})

search_simple_query_model = api.model("Biomarker Simple Search Query",
    {
        "term_category": fields.String(required=True, default="biomarker"),
        "term": fields.String(required=True, default="AN6278-5")
    }
)

detail_query_model = api.model("Biomarker Detail Query", 
    { 
        "biomarker_id": fields.String(required=True, default="AN6278-5")
    }
)

search_query_model = api.model("Biomarker Search Query",
    { 
        "biomarker_id": fields.String(required=True, default="AN6278-5"),
        "biomarker":fields.String(required=True, default="increased IL6 level"),
        "biomarker_entity_name":fields.String(required=True, default="Interleukin-6"),
        "biomarker_entity_id":fields.String(required=True, default="P05231-1"),
        "biomarker_entity_type":fields.String(required=True, default="protein"),
        "specimen_name":fields.String(required=True, default="blood"),
        "specimen_id":fields.String(required=True, default="0000178"),
        "specimen_loinc_code":fields.String(required=True, default="26881-3"),
        "best_biomarker_role":fields.String(required=True, default="prognostic"),
        "condition_id":fields.String(required=True, default="DOID:10283"),
        "condition_name":fields.String(required=True, default="prostate cancer"),
        "publication_id":fields.String(required=True, default="10914713")
    }
)



list_query_model = api.model("Biomarker List Query",{ "id": fields.String(required=True, default="")})




@api.route('/search_simple/')
class Biomarker(Resource):
    @api.doc('search_simple')
    @api.expect(search_simple_query_model)
    def post(self):
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        res_obj = {}
        try:
            req_obj = get_req_obj(request)
            res_obj = log_request(req_obj, "/biomarker/search_simple/", request)
            if "error_list" not in res_obj:
                res_obj = biomarker_search_simple(req_obj, config_obj)
        except Exception as e:
            res_obj = log_error(traceback.format_exc())
        http_code = 500 if "error_list" in res_obj else 200
        return res_obj, http_code

    @api.doc(False)
    def get(self):
        return self.post()




@api.route('/search_init/')
class Biomarker(Resource):
    @api.doc('search_init')
    @api.expect(search_init_query_model)
    def post(self):
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        res_obj = {}
        try:
            res_obj = log_request({}, "/biomarker/search_init/", request)
            if "error_list" not in res_obj:
                res_obj = biomarker_search_init(config_obj)
        except Exception as e:
            res_obj = log_error(traceback.format_exc())
        http_code = 500 if "error_list" in res_obj else 200 
        return res_obj, http_code

    @api.doc(False)
    def get(self):
        return self.post()



@api.route('/detail/<biomarker_id>/')
@api.doc(params={"biomarker_id": {"in": "query", "default": "AN6278-5"}})
class Biomarker(Resource):
    @api.doc('detail')
    @api.expect(detail_query_model)
    def post(self, biomarker_id):
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        res_obj = {}
        try:
            req_obj = {"biomarker_id":biomarker_id}
            req_obj_extra = get_req_obj(request)
            if req_obj_extra != None:
                if "paginated_tables" in req_obj_extra:
                    req_obj["paginated_tables"] = req_obj_extra["paginated_tables"]
            res_obj = log_request(req_obj, "/biomarker/detail/", request)
            if "error_list" not in res_obj:
                res_obj = biomarker_detail(req_obj, config_obj)
        except Exception as e:
            res_obj = log_error(traceback.format_exc())
        http_code = 500 if "error_list" in res_obj else 200
        return res_obj, http_code

    @api.doc(False)
    def get(self, biomarker_id):
        return self.post(biomarker_id)



@api.route('/search/')
class Biomarker(Resource):
    @api.doc('search')
    @api.expect(search_query_model)
    def post(self):
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        res_obj = {}
        try:
            req_obj = get_req_obj(request)
            res_obj = log_request(req_obj, "/biomarker/search/", request)
            if "error_list" not in res_obj:
                res_obj = biomarker_search(req_obj, config_obj)
        except Exception as e:
            res_obj = log_error(traceback.format_exc())
        http_code = 500 if "error_list" in res_obj else 200 
        return res_obj, http_code
    
    @api.doc(False)
    def get(self):
        return self.post()



@api.route('/list/')
class Biomarker(Resource):
    @api.doc('list')
    @api.expect(list_query_model)
    def post(self):
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        res_obj = {}
        try:
            req_obj = get_req_obj(request)
            res_obj = log_request(req_obj, "/biomarker/list/", request)
            if "error_list" not in res_obj:
                api_name = "biomarker_list"
                cache_id = req_obj["id"] if "id" in req_obj else ""
                listcache_id = get_hash_id(api_name, "", req_obj)
                res_obj = get_cached_result_list(cache_id, listcache_id)
                if res_obj == None:
                    res_obj = get_cached_records_indirect(req_obj, config_obj, False)
                    if "error_list" not in res_obj:
                        res = cache_result_list(cache_id, listcache_id, res_obj, config_obj)
                        if "error_list" in res:
                            res_obj = res
                if "results" in res_obj:
                    res_obj["results"] = apply_pagination(res_obj["results"], req_obj)

        except Exception as e:
            res_obj = log_error(traceback.format_exc())
        http_code = 500 if "error_list" in res_obj else 200
        return res_obj, http_code

    @api.doc(False)
    def get(self):
        return self.post()

