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

from glygen.seqmapping_apilib import search
from glygen.util import trim_object
import traceback


api = Namespace("seqmapping", description="Seqmapping APIs")

search_query_model = api.model(
    'Seq Mapping Search Query', 
    { 'query': fields.String(required=True, default="", description='')}
)

search_query_model = api.model(
    'Seq Mapping Search Query',
    {
        "glytoucan_ac_list": fields.List(fields.String(), required=True, default=["G17689DH","G01543ZX","G00009BX"])
    }
)




@api.route('/search/')
class Seqmapping(Resource):
    @api.expect(search_query_model)
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
        
        http_code = 500 if "error_list" in res_obj else 200
        return res_obj, http_code

    @api.doc(False)
    def get(self):
        return self.post()






