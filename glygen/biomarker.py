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

from glygen.biomarker_apilib import biomarker_detail
from glygen.util import get_req_obj
import traceback


api = Namespace("biomarker", description="Biomarker APIs")

detail_query_model = api.model("Biomarker Detail Query", 
    { 
        "id": fields.String(required=True, default="A0001")
    }
)


@api.route('/detail/<biomarker_id>/')
@api.doc(params={"biomarker_id": {"in": "query", "default": "A0001"}})
class Biomarker(Resource):
    @api.doc('detail')
    @api.expect(detail_query_model)
    def post(self, biomarker_id):
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        res_obj = {}
        try:
            req_obj = {"id":biomarker_id}
            req_obj_extra = get_req_obj(request)
            if req_obj_extra != None:
                if "paginated_tables" in req_obj_extra:
                    req_obj["paginated_tables"] = req_obj_extra["paginated_tables"]
            res_obj = log_request(req_obj, "/biomarker/detail/", request)
            if "error_list" not in res_obj:
                res_obj = biomarker_detail(req_obj, config_obj)
        except Exception as e:
            res_obj = log_error(traceback.format_exc())
        http_code = 500 if "error_list" in res_obj else 200
        return res_obj, http_code

    @api.doc(False)
    def get(self, biomarker_id):
        return self.post(biomarker_id)







