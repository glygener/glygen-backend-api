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

from glygen.struct_apilib import structure_detail
from glygen.util import get_req_obj
import traceback


api = Namespace("Structure", description="Structure APIs")

detail_query_model = api.model("Structure Detail Query",
    { "structure_id": fields.String(required=True, default="2qj2")}
)


@api.route('/detail/<structure_id>/')
@api.doc(params={"structure_id": {"in": "query", "default": "2qj2"}})
class Structure(Resource):
    @api.doc('detail')
    @api.expect(detail_query_model)
    def post(self, glytoucan_ac):
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        res_obj, log_obj = {}, {}
        try:
            req_obj = {"structure_id":structure_id}
            req_obj_extra = get_req_obj(request)
            if req_obj_extra != None:
                for k in req_obj_extra:
                    req_obj[k] = req_obj_extra[k]
            log_obj = log_request(req_obj, "/structure/detail/", request)
            if "error_list" not in log_obj:
                res_obj = structure_detail(req_obj, config_obj)
        except Exception as e:
            res_obj = log_error(traceback.format_exc(), log_obj)
        http_code = 500 if "error_list" in res_obj else 200
        return res_obj, http_code

    @api.doc(False)
    def get(self, structure_id):
        return self.post(structure_id)





