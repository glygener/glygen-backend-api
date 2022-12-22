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

from glygen.graph_apilib import getdata
from glygen.util import get_error_obj, trim_object
import traceback

api = Namespace("graph", description="Graph APIs")
getdata_query_model = api.model(
    'Get Data Query',
    { 'query': fields.String(required=True, default="", description='')}
)

@api.route('/getdata/')
class GRaph(Resource):
    @api.doc('getdata')
    @api.expect(getdata_query_model)
    def post(self):
        api_name = "graph_getdata"
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        res_obj = {}
        try:
            req_obj = request.json
            trim_object(req_obj)
<<<<<<< HEAD
            data_path = os.environ["DATA_PATH"]
=======
            data_path = current_app.config["DATA_PATH"]
>>>>>>> b661168d86f050c4e3f5b0a0708b45922caf2f3b
            res_obj = getdata(req_obj, config_obj)
        except Exception as e:
            log_path = current_app.config["LOG_PATH"]
            res_obj = get_error_obj(api_name, traceback.format_exc(), log_path)
        return res_obj



