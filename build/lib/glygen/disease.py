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

from glygen.disease_apilib import disease_detail, disease_search, disease_search_init, disease_search_simple
from glygen.util import get_req_obj, get_cached_records_indirect, get_hash_id, cache_result_list, get_cached_result_list, apply_pagination
import traceback



api = Namespace("disease", description="Disease APIs")


search_init_query_model = api.model("Disease Search Init Query", {})

search_simple_query_model = api.model("Disease Simple Search Query",
    {
        "term_category": fields.String(required=True, default="disease"),
        "term": fields.String(required=True, default="doid.1612")
    }
)

detail_query_model = api.model("Disease Detail Query", 
    { 
        "record_id": fields.String(required=True, default="doid.1612")
    }
)

search_query_model = api.model("Disease Search Query",
    { 
        "record_id": fields.String(required=True, default="doid.1612"),
        "disease":fields.String(required=True, default="increased IL6 level"),
        "disease_entity_name":fields.String(required=True, default="Interleukin-6"),
        "disease_entity_id":fields.String(required=True, default="P05231-1"),
        "disease_entity_type":fields.String(required=True, default="protein"),
        "specimen_name":fields.String(required=True, default="blood"),
        "specimen_id":fields.String(required=True, default="0000178"),
        "specimen_loinc_code":fields.String(required=True, default="26881-3"),
        "best_disease_role":fields.String(required=True, default="prognostic"),
        "condition_id":fields.String(required=True, default="DOID:10283"),
        "condition_name":fields.String(required=True, default="prostate cancer"),
        "publication_id":fields.String(required=True, default="10914713")
    }
)



list_query_model = api.model("Disease List Query",{ "id": fields.String(required=True, default="")})




@api.route('/search_simple/')
class Disease(Resource):
    @api.doc('search_simple')
    @api.expect(search_simple_query_model)
    def post(self):
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        res_obj = {}
        try:
            req_obj = get_req_obj(request)
            res_obj = log_request(req_obj, "/disease/search_simple/", request)
            if "error_list" not in res_obj:
                res_obj = disease_search_simple(req_obj, config_obj)
        except Exception as e:
            res_obj = log_error(traceback.format_exc())
        http_code = 500 if "error_list" in res_obj else 200
        return res_obj, http_code

    @api.doc(False)
    def get(self):
        return self.post()




@api.route('/search_init/')
class Disease(Resource):
    @api.doc('search_init')
    @api.expect(search_init_query_model)
    def post(self):
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        res_obj = {}
        try:
            res_obj = log_request({}, "/disease/search_init/", request)
            if "error_list" not in res_obj:
                res_obj = disease_search_init(config_obj)
        except Exception as e:
            res_obj = log_error(traceback.format_exc())
        http_code = 500 if "error_list" in res_obj else 200 
        return res_obj, http_code

    @api.doc(False)
    def get(self):
        return self.post()



@api.route('/detail/<record_id>/')
@api.doc(params={"record_id": {"in": "query", "default": "doid.1612"}})
class Disease(Resource):
    @api.doc('detail')
    @api.expect(detail_query_model)
    def post(self, record_id):
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        res_obj = {}
        try:
            req_obj = {"record_id":record_id}
            req_obj_extra = get_req_obj(request)
            if req_obj_extra != None:
                if "paginated_tables" in req_obj_extra:
                    req_obj["paginated_tables"] = req_obj_extra["paginated_tables"]
            res_obj = log_request(req_obj, "/disease/detail/", request)
            if "error_list" not in res_obj:
                res_obj = disease_detail(req_obj, config_obj)
        except Exception as e:
            res_obj = log_error(traceback.format_exc())
        http_code = 500 if "error_list" in res_obj else 200
        return res_obj, http_code

    @api.doc(False)
    def get(self, record_id):
        return self.post(record_id)



@api.route('/search/')
class Disease(Resource):
    @api.doc('search')
    @api.expect(search_query_model)
    def post(self):
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        res_obj = {}
        try:
            req_obj = get_req_obj(request)
            res_obj = log_request(req_obj, "/disease/search/", request)
            if "error_list" not in res_obj:
                res_obj = disease_search(req_obj, config_obj)
        except Exception as e:
            res_obj = log_error(traceback.format_exc())
        http_code = 500 if "error_list" in res_obj else 200 
        return res_obj, http_code
    
    @api.doc(False)
    def get(self):
        return self.post()



@api.route('/list/')
class Disease(Resource):
    @api.doc('list')
    @api.expect(list_query_model)
    def post(self):
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        res_obj = {}
        try:
            req_obj = get_req_obj(request)
            res_obj = log_request(req_obj, "/disease/list/", request)
            if "error_list" not in res_obj:
                api_name = "disease_list"
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

