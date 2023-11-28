import os,sys
from flask_restx import Namespace, Resource, fields
from flask import (request, current_app, send_file)
from glygen.db import log_error, log_request
from glygen.document import get_one, get_many, insert_one, update_one, delete_one, order_json_obj
from werkzeug.utils import secure_filename
import datetime
import time
import subprocess
import cgi
import json
import bcrypt

from glygen.idmapping_apilib import search_init, search
from glygen.util import get_req_obj, get_cached_records_direct
import traceback


api = Namespace("idmapping", description="ID Mapping APIs")

idmapping_search_init_query_model = api.model("ID Mapping Search Init Query", {})


idmapping_search_query_model = api.model(
    'ID Mapping Search Query',
    { 
        "recordtype": fields.String(required=True, default="protein", description=""),
        "input_namespace": fields.String(required=True, default="UniProtKB", description=""),
        "output_namespace": fields.String(required=True, default="GeneID", description=""),
        "input_idlist": fields.List(fields.String(), required=True, default=["Q9VRR2", "M9PJ12"])
    }
)


list_query_model = api.model("ID Mapping List Query",{ "id": fields.String(required=True, default="")})



@api.route('/search_init/')
class Idmapping(Resource):
    @api.expect(idmapping_search_init_query_model)
    def post(self):
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        res_obj = {}
        try:
            data_path = os.environ["DATA_PATH"]
            res_obj = log_request({}, "/idmapping/search_init/", request)
            if "error_list" not in res_obj:
                res_obj = search_init(config_obj)
        except Exception as e:
            res_obj = log_error(traceback.format_exc())
        http_code = 500 if "error_list" in res_obj else 200
        return res_obj, http_code

    @api.doc(False)
    def get(self):
        return self.post()


@api.route('/search/')
class Idmapping(Resource):
    @api.expect(idmapping_search_query_model)
    def post(self):
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        res_obj = {}
        try:
            req_obj_form = request.form
            req_obj_json = request.json
            req_obj = {}
            if req_obj_json != None:
                req_obj = req_obj_json
            else:
                for k in ["recordtype", "input_namespace", "output_namespace"]:
                    if k in req_obj_form:
                        #req_obj[k] = req_obj_form[k].value
                        req_obj[k] = req_obj_form[k]

                if "input_idlist" in req_obj_form:
                    req_obj["input_idlist"] = []
                    #tmp_str = req_obj_form["input_idlist"].value.strip()
                    tmp_str = req_obj_form["input_idlist"].strip()
                    if tmp_str != "":
                        for word in tmp_str.split(","):
                            if word.strip() not in req_obj["input_idlist"]:
                                req_obj["input_idlist"].append(word.strip())
                if "userfile" in request.files:
                    if "input_idlist" not in req_obj:
                        req_obj["input_idlist"] = []
                    file_buffer = request.files.get("userfile").read()
                    file_buffer = file_buffer.decode()
                    file_buffer = file_buffer.replace("\r", "\n").replace("\n\n", "\n")
                    line_list = file_buffer.split("\n")
                    for line in line_list:
                        if line.strip() != "":
                            for word in line.strip().split(","):
                                input_id = word.strip()
                                if input_id != "" and input_id not in req_obj["input_idlist"]:
                                    req_obj["input_idlist"].append(input_id)

            error_list = []
            for k in ["recordtype", "input_namespace", "output_namespace", "input_idlist"]:
                if k not in req_obj:
                    error_list.append({"error_code":"missing-parameter","field":k})
            if error_list != []:
                return {"error_list":error_list}
            res_obj = log_request(req_obj, "/idmapping/search/", request)
            if "error_list" not in res_obj:
                res_obj = search(req_obj, config_obj)
        except Exception as e:
            res_obj = log_error(traceback.format_exc())
        http_code = 500 if "error_list" in res_obj else 200
        return res_obj, http_code

    @api.doc(False)
    def get(self):
        return self.post()

@api.route('/list/')
class Idmapping(Resource):
    @api.expect(list_query_model)
    def post(self):
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        res_obj = {}
        try:
            req_obj = get_req_obj(request)
            res_obj = log_request(req_obj, "/idmapping/list/", request)
            if "error_list" not in res_obj:
                res_obj = get_cached_records_direct(req_obj, config_obj)
        except Exception as e:
            res_obj = log_error(traceback.format_exc())
        http_code = 500 if "error_list" in res_obj else 200
        return res_obj, http_code

    @api.doc(False)
    def get(self):
        return self.post()





