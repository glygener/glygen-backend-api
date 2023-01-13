import os,sys
from flask_restx import Namespace, Resource, fields
from flask import (request, current_app, send_file)
from glygen.document import get_one, get_many, insert_one, update_one, delete_one, order_json_obj
from werkzeug.utils import secure_filename
import datetime
import time
import subprocess
import json
import bcrypt
from flask_jwt_extended import (
    jwt_required, get_jwt_identity
)

from glygen.seqmapping_apilib import search
from glygen.util import get_error_obj, trim_object
import traceback


api = Namespace("seqmapping", description="Seqmapping APIs")

search_query_model = api.model(
    'Search Query', 
    { 'query': fields.String(required=True, default="", description='')}
)

@api.route('/search/')
class Seqmapping(Resource):
    @api.doc('search')
    @api.expect(search_query_model)
    def post(self):
        api_name = "seqmapping_search"
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        res_obj = {}
        try:
            req_obj = request.json
            trim_object(req_obj)
            res_obj = search(req_obj, config_obj)
        except Exception as e:
            log_path = current_app.config["LOG_PATH"] 
            res_obj = get_error_obj(api_name, traceback.format_exc(), log_path)
        return res_obj

    def get(self):
        return self.post()






