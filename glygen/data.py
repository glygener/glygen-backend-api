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

from glygen.data_apilib import data_download
from glygen.util import trim_object
import traceback


api = Namespace("data", description="Data APIs")

download_query_model = api.model(
    "Data Download Query", 
    { 
        "compressed": fields.Boolean(required=True, default=False),
        "type": fields.String(required=True, default="glycan_list"),
        "format": fields.String(required=True, default="csv"),
        "id": fields.String(required=True, default="")
    }
)


@api.route('/download/')
class Data(Resource):
    @api.expect(download_query_model)
    def post(self):
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
            res_obj = log_error(traceback.format_exc())
        return res_obj

    @api.doc(False)
    def get(self):
        return self.post()






