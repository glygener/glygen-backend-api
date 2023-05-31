import os,sys
from flask_restx import Namespace, Resource, fields
<<<<<<< HEAD
from flask import (request, current_app, send_file)
=======
from flask import (request, current_app, send_file, jsonify)
>>>>>>> 2.0
from glygen.db import log_error
from glygen.document import get_one, get_many, insert_one, update_one, delete_one, order_json_obj
from werkzeug.utils import secure_filename
import datetime
import time
import subprocess
import json
import bcrypt

from glygen.glycan_apilib import glycan_search_init, glycan_search, glycan_search_simple, glycan_detail, glycan_image

from glygen.util import get_cached_records_indirect, get_req_obj
import traceback


api = Namespace("glycan", description="Glycan APIs")

search_simple_query_model = api.model(
    "Glycan Simple Search Query", 
    {
        "term_category": fields.String(required=True, default="glycan"),
        "term": fields.String(required=True, default="G17689DH")
    }
)
GLYCAN_ID = api.model("GLYCAN_ID", {"glycan_id": fields.String(required=True, default="G17689DH")})
search_query_model = api.model("Glycan Search Query", {"glycan_identifier":fields.Nested(GLYCAN_ID)})
search_init_query_model = api.model("Glycan Search Init Query", {})
list_query_model = api.model("Glycan List Query",{ "id": fields.String(required=True, default="")})








@api.route('/search_init/')
class Glycan(Resource):
    @api.expect(search_init_query_model)
    def post(self):
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        res_obj = {}
        try:
            res_obj = glycan_search_init(config_obj)
        except Exception as e:
            res_obj = log_error(traceback.format_exc())
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
        res_obj = {}
        try:
            req_obj = get_req_obj(request)
            res_obj = glycan_search(req_obj, config_obj)
        except Exception as e:
            res_obj = log_error(traceback.format_exc())
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
        res_obj = {}
        try:
            req_obj = get_req_obj(request)
            res_obj = glycan_search_simple(req_obj, config_obj)
        except Exception as e:
            res_obj = log_error(traceback.format_exc())
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
        res_obj = {}
        try:
            req_obj = get_req_obj(request)
            res_obj = get_cached_records_indirect(req_obj, config_obj)
        except Exception as e:
            res_obj = log_error(traceback.format_exc())
        http_code = 500 if "error_list" in res_obj else 200
        return res_obj, http_code

    @api.doc(False)
    def get(self):
        return self.post()

@api.route('/detail/<glytoucan_ac>/')
@api.doc(params={"glytoucan_ac": {"in": "query", "default": "G17689DH"}})
class Glycan(Resource):
    @api.doc('detail')
    def post(self, glytoucan_ac):
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        res_obj = {}
        try:
            req_obj = {"glytoucan_ac":glytoucan_ac}
            res_obj = glycan_detail(req_obj, config_obj)
            #res_obj = jsonify(res_obj)
        except Exception as e:
            res_obj = log_error(traceback.format_exc())
        http_code = 500 if "error_list" in res_obj else 200
        return res_obj, http_code
<<<<<<< HEAD
   
=======

>>>>>>> 2.0
    @api.doc(False)
    def get(self, glytoucan_ac):
        return self.post(glytoucan_ac)


@api.route('/image/<glytoucan_ac>/')
@api.doc(params={"glytoucan_ac": {"in": "query", "default": "G17689DH"}})
class Glycan(Resource):
    @api.doc('image')
    def post(self, glytoucan_ac):
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        res_obj = {}
        try:
            req_obj = {"glytoucan_ac":glytoucan_ac}
            data_path = os.environ["DATA_PATH"]
            img_file = glycan_image(req_obj, data_path)
            return send_file(img_file, mimetype='image/png')
        except Exception as e:
            res_obj = log_error(traceback.format_exc())
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
        res_obj = {}
        try:
            downloads_path = os.environ["DOWNLOADS_PATH"]
            pdb_file = downloads_path + "glycam_3d/glycan/current/%s.pdb" % (glytoucan_ac)
            if os.path.isfile(pdb_file) == False:
                return {"error_list":[{"error_code":"non-existent-record"}]}
            return send_file(pdb_file, mimetype='plain/text')
        except Exception as e:
            res_obj = log_error(traceback.format_exc())
        http_code = 500 if "error_list" in res_obj else 200
        return res_obj, http_code

    @api.doc(False)
    def get(self, glytoucan_ac):
        return self.post(glytoucan_ac)




