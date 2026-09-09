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
from glygen.db import get_mongodb
from glygen.util import trim_object, get_req_obj
import traceback

api = Namespace("species", description="Species APIs")
search_init_query_model = api.model(
    'Species Search Init Query',
    {}
)


@api.route('/search_init/')
class Species(Resource):
    @api.expect(search_init_query_model)
    def post(self):
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        res_obj, log_obj = {}, {}
        try:
            res_obj = {"species":[]}
            req_obj = get_req_obj(request)
            log_obj = log_request(req_obj, "/species/search_init/", request)
            if "error_list" not in log_obj:
                dbh, error_obj = get_mongodb()
                if error_obj != {}:
                    return error_obj
                for doc in dbh["c_species"].find({}):
                    if "_id" in doc:
                        doc.pop("_id")
                    if "evidence" in doc:
                        doc.pop("evidence")
                    res_obj["species"].append(doc) 
        except Exception as e:
            res_obj = log_error(traceback.format_exc(), log_obj)
        http_code = 500 if "error_list" in res_obj else 200
        return res_obj, http_code

    @api.doc(False)
    def get(self):
        return self.post()












