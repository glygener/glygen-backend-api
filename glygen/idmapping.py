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

from glygen.idmapping_apilib import search_init, search
from glygen.util import trim_object, get_cached_records_direct
import traceback


api = Namespace("idmapping", description="ID Mapping APIs")

idmapping_search_init_query_model = api.model("ID Mapping Search Init Query", {})


idmapping_search_query_model = api.model(
    'ID Mapping Search Query',
    { 
        "recordtype": fields.String(required=True, default="protein", description=""),
        "input_namespace": fields.String(required=True, default="UniProtKB", description=""),
        "output_namespace": fields.String(required=True, default="GeneID", description=""),
        "input_idlist": fields.List(fields.String(), required=True, default=["Q9VRR2", "M9PJ12"])
    }
)

list_query_model = api.model("ID Mapping List Query",{ "id": fields.String(required=True, default="")})



@api.route('/search_init/')
class Idmapping(Resource):
    @api.expect(idmapping_search_init_query_model)
    def post(self):
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        res_obj = {}
        try:
            data_path = os.environ["DATA_PATH"]
            res_obj = search_init(config_obj)
        except Exception as e:
            res_obj = log_error(traceback.format_exc())
        return res_obj

    @api.doc(False)
    def get(self):
        return self.post()


@api.route('/search/')
class Idmapping(Resource):
    @api.expect(idmapping_search_query_model)
    def post(self):
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        res_obj = {}
        try:
            req_obj = request.json
            trim_object(req_obj)
            res_obj = search(req_obj, config_obj)
        except Exception as e:
            res_obj = log_error(traceback.format_exc())
        return res_obj

    @api.doc(False)
    def get(self):
        return self.post()

@api.route('/list/')
class Idmapping(Resource):
    @api.expect(list_query_model)
    def post(self):
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        res_obj = {}
        try:
            req_obj = request.json
            trim_object(req_obj)
            res_obj = get_cached_records_direct(req_obj, config_obj)
        except Exception as e:
            res_obj = log_error(traceback.format_exc())
        return res_obj

    @api.doc(False)
    def get(self):
        return self.post()





