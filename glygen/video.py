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

from glygen.video_apilib import video_addnew, video_detail, video_list, video_delete

from glygen.util import get_req_obj
import traceback

api = Namespace("video", description="Video APIs")

addnew_query_model = api.model(
    'Video Addnew Query', 
    { 
        "url": fields.String(required=True, default="https://www.youtube.com/embed/xyV5v5nRm6A?rel=0")
    }
)
<<<<<<< HEAD
=======



>>>>>>> 2.0
detail_query_model = api.model(
    'Video Detail Query', { "id": fields.String(required=True, default="63d04393d634c7d21067b32e")}
)
list_query_model = api.model('Video List Query', {})
delete_query_model = api.model(
    'Video Delete Query', { "id": fields.String(required=True, default="63d04393d634c7d21067b32e")}
)



@api.route('/addnew/')
class Video(Resource):
<<<<<<< HEAD
    @api.doc(False)
=======
>>>>>>> 2.0
    @api.expect(addnew_query_model)
    @jwt_required
    def post(self):
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        res_obj = {}
        try:
            req_obj = get_req_obj(request)
            #current_user, user_info = "rykahsay@gwu.edu", {}
            current_user = get_jwt_identity()
            res_obj = video_addnew(current_user, req_obj, config_obj)
        except Exception as e:
            res_obj = log_error(traceback.format_exc())
        http_code = 500 if "error_list" in res_obj else 200
        return res_obj, http_code

    @api.doc(False)
    def get(self):
        return self.post()


@api.route('/detail/')
class Video(Resource):
    @api.expect(detail_query_model)
    def post(self):
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        res_obj = {}
        try:
            req_obj = get_req_obj(request)
            res_obj = video_detail(req_obj, config_obj)
        except Exception as e:
            res_obj = log_error(traceback.format_exc())
        http_code = 500 if "error_list" in res_obj else 200
        return res_obj, http_code

    @api.doc(False)
    def get(self):
        return self.post()

@api.route('/list/')
class Video(Resource):
    @api.expect(list_query_model)
    def post(self):
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        res_obj = {}
        try:
            req_obj = get_req_obj(request)
            res_obj = video_list(req_obj, config_obj)
        except Exception as e:
            res_obj = log_error(traceback.format_exc())
        http_code = 500 if "error_list" in res_obj else 200
        return res_obj, http_code

    @api.doc(False)
    def get(self):
        return self.post()

@api.route('/delete/')
class Video(Resource):
<<<<<<< HEAD
    @api.doc(False)
=======
    #@api.doc(False)
>>>>>>> 2.0
    @api.expect(delete_query_model)
    @jwt_required
    def post(self):
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        res_obj = {}
        try:
            req_obj = get_req_obj(request)
            #current_user, user_info = "rykahsay@gwu.edu", {}
            current_user = get_jwt_identity()
            res_obj = video_delete(current_user, req_obj, config_obj)
        except Exception as e:
            res_obj = log_error(traceback.format_exc())
        http_code = 500 if "error_list" in res_obj else 200
        return res_obj, http_code

    @api.doc(False)
    def get(self):
        return self.post()






