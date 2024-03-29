import os,sys
from flask_restx import Namespace, Resource, fields
from flask import (request, current_app, send_file)
from glygen.db import log_error, log_request
from glygen.document import get_one, get_many, insert_one, update_one, delete_one, order_json_obj
from werkzeug.utils import secure_filename
import datetime
import time
import subprocess
import json
import bcrypt

from glygen.pages_apilib import home_init
from glygen.util import trim_object
import traceback


api = Namespace("pages", description="Pages APIs")


home_init_query_model = api.model("Pages Init Query", {})


@api.route('/home_init/')
class Pages(Resource):
    @api.expect(home_init_query_model)
    def post(self):
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        res_obj = {}
        try:
            data_path = os.environ["DATA_PATH"]
            res_obj = log_request({}, "/pages/home_init/", request)
            if "error_list" not in res_obj:
                res_obj = home_init(config_obj, data_path)
        except Exception as e:
            res_obj = log_error(traceback.format_exc())
        
        http_code = 500 if "error_list" in res_obj else 200
        return res_obj, http_code
        
    @api.doc(False)
    def get(self):
        return self.post()






