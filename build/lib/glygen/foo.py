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

from glygen.foo_apilib import foo_yyy1, foo_yyy2
from glygen.util import get_error_obj, trim_object
import traceback


api = Namespace("foo", description="Foo APIs")

yyy1_query_model = api.model(
    'Yyy1 Query', 
    { 'query': fields.String(required=True, default="", description='')}
)

@api.route('/yyy1/')
class Data(Resource):
    @api.doc('yyy1')
    @api.expect(yyy1_query_model)
    def post(self):
        api_name = "foo_yyy1"
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        res_obj = {}
        try:
            req_obj = request.json
            trim_object(req_obj)
            data_path = os.environ["DATA_PATH"]
            res_obj = foo_yyy1(req_obj, config_obj, data_path)
        except Exception as e:
            log_path = os.environ["DATA_PATH"] + "/logs"
            res_obj = get_error_obj(api_name, traceback.format_exc(), log_path)
        return res_obj







