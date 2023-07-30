import os,sys
from flask_restx import Namespace, Resource, fields
from flask import (request, current_app)
from glygen.db import log_error, log_request
from glygen.document import get_one, get_many, insert_one, update_one, delete_one, order_json_obj
from werkzeug.utils import secure_filename
import datetime
import time
import subprocess
import json
import bcrypt

from glygen.site_apilib import site_search_init, site_detail
from glygen.util import trim_object, get_req_obj
import traceback


api = Namespace("site", description="Site APIs")
search_init_query_model = api.model(
    'Site Search Init Query',
    {}
)

@api.route('/search_init/')
class Site(Resource):
    @api.expect(search_init_query_model)
    def post(self):
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        res_obj = {}
        try:
            res_obj = log_request({}, "/site/search_init/", request)
            if "error_list" not in res_obj:
                res_obj = site_search_init(config_obj)
        except Exception as e:
            res_obj = log_error(traceback.format_exc())
        http_code = 500 if "error_list" in res_obj else 200
        return res_obj, http_code

    @api.doc(False)
    def get(self):
        return self.post()


@api.route('/detail/<site_id>/')
@api.doc(params={"site_id": {"in": "query", "default": "P02724-1.52.52"}})
class Site(Resource):
    def post(self, site_id):
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        res_obj = {}
        try:
            req_obj = {"site_id":site_id}
            req_obj_extra = get_req_obj(request)
            if req_obj_extra != None:
                if "paginated_tables" in req_obj_extra:
                    req_obj["paginated_tables"] = req_obj_extra["paginated_tables"]
            res_obj = log_request(req_obj, "/site/detail/", request)
            if "error_list" not in res_obj:
                res_obj = site_detail(req_obj, config_obj)
        except Exception as e:
            res_obj = log_error(traceback.format_exc())
        http_code = 500 if "error_list" in res_obj else 200
        return res_obj, http_code

    @api.doc(False)
    def get(self, site_id):
        return self.post(site_id)





