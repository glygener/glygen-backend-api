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

from glygen.indexlib import search_one
from glygen.protein_apilib import protein_search_init, protein_search, protein_detail, protein_alignment, search_simple
from glygen.util import make_list_objects_indirect, get_req_obj, cache_list_objects, get_hash_id, retrieve_cached_list_objects, apply_pagination
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
detail_query_model = api.model("Protein Detail Query",
    {
        "uniprot_canonical_ac": fields.String(required=True, default="P14210-1")
    }
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
            res_obj = log_request({}, "/protein/search_init/", request)
            if "error_list" not in res_obj:
                res_obj = protein_search_init(config_obj)
        except Exception as e:
            res_obj = log_error(traceback.format_exc())
        http_code = 500 if "error_list" in res_obj else 200 
        return res_obj, http_code

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
            req_obj = get_req_obj(request)
            res_obj = log_request(req_obj, "/protein/search/", request)
            if "error_list" not in res_obj:
                res_obj = protein_search(req_obj, config_obj)
        except Exception as e:
            res_obj = log_error(traceback.format_exc())
        http_code = 500 if "error_list" in res_obj else 200 
        return res_obj, http_code
    
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
            req_obj = get_req_obj(request)
            res_obj = log_request(req_obj, "/protein/search_simple/", request)
            if "error_list" not in res_obj:
                cache_flag, exact_match_flag = True, True
                res_obj = search_one("protein_search_simple",req_obj,config_obj,cache_flag,exact_match_flag)
        except Exception as e:
            res_obj = log_error(traceback.format_exc())
        http_code = 500 if "error_list" in res_obj else 200
        return res_obj, http_code

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
            req_obj = get_req_obj(request)
            res_obj = log_request(req_obj, "/protein/list/", request)
            if "error_list" not in res_obj:
                api_name = "protein_list"
                cache_id = req_obj["id"] if "id" in req_obj else ""
                listcache_id = get_hash_id(api_name, "", req_obj)
                in_dict = {"cache_id":cache_id,"listcache_id":listcache_id,"api_name":api_name}
                res_obj = retrieve_cached_list_objects(in_dict,req_obj,config_obj,"paginated")
                #return {"n":len(res_obj["results"]), "obj":res_obj["results"][0]}
                #return {"aa":res_obj, "apiname":api_name, "reqobj":req_obj, "listcacheid":listcache_id}
                #return {"listcacheid":listcache_id, "cache_coll":res_obj["cache_coll"]}
                if res_obj == None:
                    res_obj = make_list_objects_indirect(req_obj, config_obj, False)
                    #return res_obj
                    if "error_list" not in res_obj:
                        list_size = res_obj["pagination"]["total_length"]
                        res = cache_list_objects(api_name, cache_id, listcache_id, res_obj, config_obj)
                        if "error_list" in res:
                            res_obj = res
                        else:
                            res_obj = retrieve_cached_list_objects(in_dict,req_obj,config_obj,"paginated")
                    #if "results" in res_obj:
                    #    res_obj["results"] = apply_pagination(res_obj["results"], req_obj)

        except Exception as e:
            res_obj = log_error(traceback.format_exc())
        http_code = 500 if "error_list" in res_obj else 200
        return res_obj, http_code

    @api.doc(False)
    def get(self):
        return self.post()



@api.route('/detail/<uniprot_canonical_ac>/')
@api.doc(params={"uniprot_canonical_ac": {"in": "query", "default": "P14210"}})
#@api.route('/detail/')
class Protein(Resource):
    @api.doc('detail')
    @api.expect(detail_query_model)
    def post(self, uniprot_canonical_ac):
    #def post(self):
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        json_url = os.path.join(SITE_ROOT, "conf/filter_init.json")
        config_obj["filter_init"] = json.load(open(json_url))
        res_obj = {}
        try:
            req_obj = {"uniprot_canonical_ac":uniprot_canonical_ac}
            req_obj_extra = get_req_obj(request)
            if req_obj_extra != None:
                for k in req_obj_extra:
                    req_obj[k] = req_obj_extra[k]
            res_obj = log_request(req_obj, "/protein/detail/", request)
            if "error_list" not in res_obj:
                res_obj = protein_detail(req_obj, config_obj)
        except Exception as e:
            res_obj = log_error(traceback.format_exc())
        http_code = 500 if "error_list" in res_obj else 200
        return res_obj, http_code

    @api.doc(False)
    def get(self, uniprot_canonical_ac):
    #def get(self):
        return self.post(uniprot_canonical_ac)
        #return self.post()

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
            req_obj = get_req_obj(request)
            res_obj = log_request(req_obj, "/protein/alignment/", request)
            if "error_list" not in res_obj:
                res_obj = protein_alignment(req_obj, config_obj)
        except Exception as e:
            res_obj = log_error(traceback.format_exc())
        http_code = 500 if "error_list" in res_obj else 200
        return res_obj, http_code

    @api.doc(False)
    def get(self):
        return self.post()





