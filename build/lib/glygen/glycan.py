import os,sys
from flask_restx import Namespace, Resource, fields
from flask import (request, current_app, send_file, jsonify)
from glygen.db import log_error, log_request, get_mongodb
from glygen.document import get_one, get_many, insert_one, update_one, delete_one, order_json_obj
from werkzeug.utils import secure_filename
import datetime
import time
import subprocess
import json
import bcrypt

from glygen.indexlib import search_one
from glygen.glycan_apilib import glycan_search_init, glycan_search, search_simple, glycan_detail, glycan_image, glycan_image_svg, glycan_image_metadata, glycan_sequence2ac

from glygen.util import make_list_objects_indirect, get_req_obj, get_hash_id, retrieve_cached_list_objects, cache_list_objects, apply_pagination, get_errors_in_query
from glygen.graphlib import get_graph_record
import traceback


api = Namespace("glycan", description="Glycan APIs")

search_simple_query_model = api.model(
    "Glycan Simple Search Query", 
    {
        "term_category": fields.String(required=True, default="glycan"),
        "term": fields.String(required=True, default="G17689DH")
    }
)
sequence2ac_query_model = api.model(
    "Glycan Sequence2Ac Query",
    {
        "type": fields.String(required=True, default="GlycoCT"),
        "seq": fields.String(required=True, default="RES 1b:b-dglc-HEX-1:5 2s:n-acetyl 3b:b-dglc-HEX-1:5 4s:n-acetyl 5b:b-dman-HEX-1:5 6b:a-dman-HEX-1:5 7b:b-dglc-HEX-1:5 8s:n-acetyl 9b:b-dgal-HEX-1:5 10b:a-dgro-dgal-NON-2:6|1:a|2:keto|3:d 11s:n-acetyl 12b:a-dman-HEX-1:5 13b:b-dglc-HEX-1:5 14s:n-acetyl 15b:b-dgal-HEX-1:5 16b:a-dgro-dgal-NON-2:6|1:a|2:keto|3:d 17s:n-acetyl 18b:a-lgal-HEX-1:5|6:d LIN 1:1d(2+1)2n 2:1o(4+1)3d 3:3d(2+1)4n 4:3o(4+1)5d 5:5o(3+1)6d 6:6o(2+1)7d 7:7d(2+1)8n 8:7o(4+1)9d 9:9o(3+2)10d 10:10d(5+1)11n 11:5o(6+1)12d 12:12o(2+1)13d 13:13d(2+1)14n 14:13o(4+1)15d 15:15o(3+2)16d 16:16d(5+1)17n 17:1o(6+1)18d")
    }
)

GLYCAN_ID = api.model("GLYCAN_ID", {"glycan_id": fields.String(required=True, default="G17689DH")})
search_query_model = api.model("Glycan Search Query", {"glycan_identifier":fields.Nested(GLYCAN_ID)})
search_init_query_model = api.model("Glycan Search Init Query", {})
detail_query_model = api.model("Glycan Detail Query",
    { "glytoucan_ac": fields.String(required=True, default="G17689DH")}
)
graph_query_model = api.model("Glycan Graph Query",
    { "record_id": fields.String(required=True, default="G17689DH")}
)
list_query_model = api.model("Glycan List Query",{ "id": fields.String(required=True, default="")})








@api.route('/search_init/')
class Glycan(Resource):
    @api.expect(search_init_query_model)
    def post(self):
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        res_obj, log_obj = {}, {}
        try:
            req_obj = get_req_obj(request)
            log_obj = log_request(req_obj, "/glycan/search_init/", request)
            if "error_list" not in log_obj:
                res_obj = glycan_search_init(config_obj)
        except Exception as e:
            res_obj = log_error(traceback.format_exc(), log_obj)
        http_code = 500 if "error_list" in res_obj else 200 
        return res_obj, http_code

    @api.doc(False)
    def get(self):
        return self.post()

@api.route('/search/')
class Glycan(Resource):
    @api.expect(search_query_model)
    def post(self):
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        res_obj, log_obj = {}, {}
        try:
            req_obj = get_req_obj(request)
            log_obj = log_request(req_obj, "/glycan/search/", request)
            if "error_list" not in log_obj:
                res_obj = glycan_search(req_obj, config_obj)
        except Exception as e:
            res_obj = log_error(traceback.format_exc(), log_obj)
        http_code = 500 if "error_list" in res_obj else 200 
        return res_obj, http_code

    @api.doc(False) 
    def get(self):
        return self.post()


@api.route('/search_simple/')
class Glycan(Resource):
    @api.expect(search_simple_query_model)
    def post(self):
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        res_obj, log_obj = {}, {}
        try:
            req_obj = get_req_obj(request)
            log_obj = log_request(req_obj, "/glycan/search_simple/", request)
            if "error_list" not in log_obj:
                cache_flag, exact_match_flag = True, True 
                res_obj = search_one("glycan_search_simple",req_obj,config_obj,cache_flag,exact_match_flag)
        except Exception as e:
            res_obj = log_error(traceback.format_exc(), log_obj)
        http_code = 500 if "error_list" in res_obj else 200
        return res_obj, http_code
    
    @api.doc(False)
    def get(self):
        return self.post()


@api.route('/sequence2ac/')
class Glycan(Resource):
    @api.expect(sequence2ac_query_model)
    def post(self):
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        res_obj, log_obj = {}, {}
        try:
            req_obj = get_req_obj(request)
            log_obj = log_request(req_obj, "/glycan/sequence2ac/", request)
            if "error_list" not in log_obj:
                res_obj = glycan_sequence2ac(req_obj, config_obj)
        except Exception as e:
            res_obj = log_error(traceback.format_exc(), log_obj)
        http_code = 500 if "error_list" in res_obj else 200
        return res_obj, http_code

    @api.doc(False)
    def get(self):
        return self.post()


@api.route('/list/')
class Glycan(Resource):
    @api.doc('list')
    @api.expect(list_query_model)
    def post(self):
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        res_obj, log_obj = {}, {}
        try:
            req_obj = get_req_obj(request)
            log_obj = log_request(req_obj, "/glycan/list/", request)
            if "error_list" not in log_obj:
                api_name = "glycan_list"
                cache_id = req_obj["id"] if "id" in req_obj else ""
                listcache_id = get_hash_id(api_name, "", req_obj)
                #return {"listcache_id":listcache_id, "api_name":api_name, "req":req_obj}
                in_dict = {"cache_id":cache_id,"listcache_id":listcache_id,"api_name":api_name}
                res_obj = retrieve_cached_list_objects(in_dict,req_obj,config_obj,"paginated")
                #res_obj["results"] = res_obj["results"][0:2]
                #return {"listcache_id":listcache_id, "api_name":api_name, "req":req_obj, "res":res_obj}
                if res_obj == None:
                    res_obj = make_list_objects_indirect(req_obj, config_obj, False)
                    if "error_list" not in res_obj:
                        res = cache_list_objects(api_name, cache_id, listcache_id, res_obj, config_obj)
                        if "error_list" in res:
                            res_obj = res
                        else:
                            res_obj = retrieve_cached_list_objects(in_dict,req_obj,config_obj,"paginated")
                    #if "results" in res_obj:
                    #    res_obj["results"] = apply_pagination(res_obj["results"], req_obj)
        except Exception as e:
            res_obj = log_error(traceback.format_exc(), log_obj)
        http_code = 500 if "error_list" in res_obj else 200
        return res_obj, http_code

    @api.doc(False)
    def get(self):
        return self.post()

@api.route('/detail/<glytoucan_ac>/')
@api.doc(params={"glytoucan_ac": {"in": "query", "default": "G17689DH"}})
class Glycan(Resource):
    @api.doc('detail')
    @api.expect(detail_query_model)
    def post(self, glytoucan_ac):
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        res_obj, log_obj = {}, {}
        try:
            req_obj = {"glytoucan_ac":glytoucan_ac}
            req_obj_extra = get_req_obj(request)
            if req_obj_extra != None:
                for k in req_obj_extra:
                    req_obj[k] = req_obj_extra[k]
            log_obj = log_request(req_obj, "/glycan/detail/", request)
            if "error_list" not in log_obj:
                res_obj = glycan_detail(req_obj, config_obj)
            #res_obj = jsonify(res_obj)
        except Exception as e:
            res_obj = log_error(traceback.format_exc(), log_obj)
        http_code = 500 if "error_list" in res_obj else 200
        return res_obj, http_code

    @api.doc(False)
    def get(self, glytoucan_ac):
    #def get(self):
        #return self.post()
        return self.post(glytoucan_ac)



@api.route('/graph/<record_id>/')
@api.doc(params={"record_id": {"in": "query", "default": "G17689DH"}})
class Glycan(Resource):
    @api.doc('detail')
    @api.expect(graph_query_model)
    def post(self, record_id):
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        res_obj, log_obj = {}, {}
        try:
            req_obj = {"record_id":record_id}
            log_obj = log_request(req_obj, "/glycan/graph/", request)
            if "error_list" not in log_obj:
                error_list = get_errors_in_query("glycan_graph",req_obj, config_obj)
                if error_list != []:
                    return {"error_list":error_list}
                res_obj = get_graph_record(req_obj, config_obj)
        except Exception as e:
            res_obj = log_error(traceback.format_exc(), log_obj)
        http_code = 500 if "error_list" in res_obj else 200
        return res_obj, http_code
    @api.doc(False)
    def get(self, record_id):
        return self.post(record_id)




@api.route('/image/<glytoucan_ac>/')
@api.doc(params={"glytoucan_ac": {"in": "query", "default": "G17689DH"}})
class Glycan(Resource):
    @api.doc('image')
    def post(self, glytoucan_ac):
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        res_obj, log_obj = {}, {}
        try:
            req_obj = {"glytoucan_ac":glytoucan_ac}
            log_obj = log_request(req_obj, "/glycan/image/", request)
            if "error_list" not in log_obj:
                data_path = os.environ["DATA_PATH"]
                img_file = glycan_image(req_obj, data_path)
                return send_file(img_file, mimetype="image/png")
        except Exception as e:
            res_obj = log_error(traceback.format_exc(), log_obj)
        http_code = 500 if "error_list" in res_obj else 200
        return res_obj, http_code

    @api.doc(False)
    def get(self, glytoucan_ac):
        return self.post(glytoucan_ac)

@api.route('/image_svg/<glytoucan_ac>/')
@api.doc(params={"glytoucan_ac": {"in": "query", "default": "G17689DH"}})
class Glycan(Resource):
    @api.doc('image_svg')
    def post(self, glytoucan_ac):
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        res_obj, log_obj = {}, {}
        try:
            req_obj = {"glytoucan_ac":glytoucan_ac}
            log_obj = log_request(req_obj, "/glycan/image_svg/", request)
            if "error_list" not in log_obj:
                data_path = os.environ["DATA_PATH"]
                img_file = glycan_image_svg(req_obj, data_path)
                return send_file(img_file, mimetype="image/svg")
        except Exception as e:
            res_obj = log_error(traceback.format_exc(), log_obj)
        http_code = 500 if "error_list" in res_obj else 200
        return res_obj, http_code
    @api.doc(False)
    def get(self, glytoucan_ac):
        return self.post(glytoucan_ac)


@api.route('/image_metadata/<glytoucan_ac>/')
@api.doc(params={"glytoucan_ac": {"in": "query", "default": "G17689DH"}})
class Glycan(Resource):
    @api.doc('image_metadata')
    def post(self, glytoucan_ac):
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        res_obj, log_obj = {}, {}
        try:
            req_obj = {"glytoucan_ac":glytoucan_ac}
            log_obj = log_request(req_obj, "/glycan/image_metadata/", request)
            if "error_list" not in log_obj:
                data_path = os.environ["DATA_PATH"]
                res_obj = glycan_image_metadata(req_obj, data_path)
                return res_obj
        except Exception as e:
            res_obj = log_error(traceback.format_exc(), log_obj)
        http_code = 500 if "error_list" in res_obj else 200
        return res_obj, http_code
    @api.doc(False)
    def get(self, glytoucan_ac):
        return self.post(glytoucan_ac)



@api.route('/pdb/<glytoucan_ac>/')
@api.doc(params={"glytoucan_ac": {"in": "query", "default": "G17689DH"}})
class Glycan(Resource):
    @api.doc('pdb')
    def post(self, glytoucan_ac):
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        res_obj, log_obj = {}, {}
        try:
            downloads_path = os.environ["DOWNLOADS_PATH"]
            pdb_file = downloads_path + "pdb_glycam/current/%s.pdb" % (glytoucan_ac)
            if os.path.isfile(pdb_file) == False:
                return {"error_list":[{"error_code":"non-existent-record"}]}
            return send_file(pdb_file, mimetype='plain/text')
        except Exception as e:
            res_obj = log_error(traceback.format_exc(), log_obj)
        http_code = 500 if "error_list" in res_obj else 200
        return res_obj, http_code

    @api.doc(False)
    def get(self, glytoucan_ac):
        return self.post(glytoucan_ac)




