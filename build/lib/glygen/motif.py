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

from glygen.motif_apilib import motif_detail
from glygen.util import trim_object, get_cached_motif_records_direct
import traceback


api = Namespace("motif", description="Motif APIs")



detail_query_model = api.model(
    'Motif Detail Query', 
    { 
        "motif_ac": fields.String(required=True, default="GGM.000115"),
        "offset": fields.Integer(required=True, default=1)
    }
)
list_query_model = api.model(
    'Motif List Query',
    { 
        "sort": fields.String(required=True, default="glycan_count"),
        "order": fields.String(required=True, default="desc")
    }
)



@api.route('/detail/')
class Motif(Resource):
    @api.doc('detail')
    @api.expect(detail_query_model)
    def post(self):
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        res_obj = {}
        try:
            req_obj = request.json
            trim_object(req_obj)
            res_obj = motif_detail(req_obj, config_obj)
        except Exception as e:
            res_obj = log_error(traceback.format_exc())
        
        http_code = 500 if "error_list" in res_obj else 200
        return res_obj, http_code

    @api.doc(False)
    def get(self):
        return self.post()


@api.route('/list/')
class Motif(Resource):
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
            res_obj = get_cached_motif_records_direct(req_obj, config_obj)
        except Exception as e:
            res_obj = log_error(traceback.format_exc())
        http_code = 500 if "error_list" in res_obj else 200
        return res_obj, http_code

    @api.doc(False)
    def get(self):
        return self.post()





