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

from glygen.video_apilib import video_addnew, video_detail, video_list, video_delete

from glygen.util import get_error_obj, trim_object
import traceback


api = Namespace("video", description="Video APIs")

addnew_query_model = api.model(
    'Addnew Query', { 'query': fields.String(required=True, default="", description='')})
detail_query_model = api.model(
    'Detail Query', { 'query': fields.String(required=True, default="", description='')})
list_query_model = api.model(
    'List Query', { 'query': fields.String(required=True, default="", description='')})
delete_query_model = api.model(
    'Delete Query', { 'query': fields.String(required=True, default="", description='')})



@api.route('/addnew/')
class Video(Resource):
    @api.doc('addnew')
    @api.expect(addnew_query_model)
    #@jwt_required
    def post(self):
        api_name = "video_addnew"
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        res_obj = {}
        try:
            req_obj = request.json
            trim_object(req_obj)
            current_user, user_info = "rykahsay@gwu.edu", {}
            #current_user = get_jwt_identity()
            #user_info, err_obj, status = get_userinfo(current_user)
            #if status == 0:
            #    return err_obj
            res_obj = video_addnew(current_user, req_obj, config_obj)
        except Exception as e:
            log_path = current_app.config["LOG_PATH"] 
            res_obj = get_error_obj(api_name, traceback.format_exc(), log_path)
        return res_obj

@api.route('/detail/')
class Video(Resource):
    @api.doc('detail')
    @api.expect(detail_query_model)
    def post(self):
        api_name = "video_detail"
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        res_obj = {}
        try:
            req_obj = request.json
            trim_object(req_obj)
            res_obj = video_detail(req_obj, config_obj)
        except Exception as e:
            log_path = current_app.config["LOG_PATH"]
            res_obj = get_error_obj(api_name, traceback.format_exc(), log_path)
        return res_obj


@api.route('/list/')
class Video(Resource):
    @api.doc('list')
    @api.expect(list_query_model)
    def post(self):
        api_name = "video_list"
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        res_obj = {}
        try:
            req_obj = request.json
            trim_object(req_obj)
            res_obj = video_list(req_obj, config_obj)
        except Exception as e:
            log_path = current_app.config["LOG_PATH"]
            res_obj = get_error_obj(api_name, traceback.format_exc(), log_path)
        return res_obj

@api.route('/delete/')
class Video(Resource):
    @api.doc('delete')
    @api.expect(delete_query_model)
    #@jwt_required
    def post(self):
        api_name = "video_delete"
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        res_obj = {}
        try:
            req_obj = request.json
            trim_object(req_obj)
            current_user, user_info = "rykahsay@gwu.edu", {}
            #current_user = get_jwt_identity()
            #user_info, err_obj, status = get_userinfo(current_user)
            #if status == 0:
            #    return err_obj
            res_obj = video_delete(current_user, req_obj, config_obj)
        except Exception as e:
            log_path = current_app.config["LOG_PATH"]
            res_obj = get_error_obj(api_name, traceback.format_exc(), log_path)
        return res_obj






