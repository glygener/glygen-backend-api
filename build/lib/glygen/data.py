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

from glygen.data_apilib import data_download
from glygen.util import get_error_obj, trim_object
import traceback


api = Namespace("data", description="Data APIs")

download_query_model = api.model(
    'Download Query', 
    { 'query': fields.String(required=True, default="", description='')}
)

@api.route('/download/')
class Data(Resource):
    @api.doc('download')
    @api.expect(download_query_model)
    def post(self):
        api_name = "data_download"
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        res_obj = {}
        try:
            req_obj = request.json
            trim_object(req_obj)
            data_path = os.environ["DATA_PATH"]
            res_obj = data_download(req_obj, config_obj, data_path)
        except Exception as e:
            log_path = current_app.config["LOG_PATH"] 
            res_obj = get_error_obj(api_name, traceback.format_exc(), log_path)
        return res_obj







