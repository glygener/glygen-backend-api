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
from flask_jwt_extended import (
    jwt_required, get_jwt_identity
)

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
            req_obj = request.json
            trim_object(req_obj)
            data_path = os.environ["DATA_PATH"]
            res_obj = home_init(config_obj, data_path)
        except Exception as e:
            res_obj = log_error(traceback.format_exc())
        return res_obj

    @api.doc(False)
    def get(self):
        return self.post()






