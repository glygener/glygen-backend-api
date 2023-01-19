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

from glygen.event_apilib import event_addnew, event_detail, event_update, event_list, event_delete

from glygen.util import get_error_obj, trim_object
import traceback


api = Namespace("event", description="Event APIs")

addnew_query_model = api.model(
    'Addnew Query', { 'query': fields.String(required=True, default="", description='')})
detail_query_model = api.model(
    'Detail Query', { 'query': fields.String(required=True, default="", description='')})
list_query_model = api.model(
    'List Query', { 'query': fields.String(required=True, default="", description='')})
update_query_model = api.model(
    'Update Query', { 'query': fields.String(required=True, default="", description='')})

delete_query_model = api.model(
    'Delete Query', { 'query': fields.String(required=True, default="", description='')})




@api.route('/addnew/')
class Event(Resource):
    @api.doc('addnew')
    @api.expect(addnew_query_model)
    #@jwt_required
    def post(self):
        api_name = "event_addnew"
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
            res_obj = event_addnew(current_user, req_obj, config_obj)
        except Exception as e:
            log_path = current_app.config["LOG_PATH"] 
            res_obj = get_error_obj(api_name, traceback.format_exc(), log_path)
        return res_obj

    @api.doc(False)
    def get(self):
        return self.post()


@api.route('/detail/')
class Event(Resource):
    @api.doc('detail')
    @api.expect(detail_query_model)
    def post(self):
        api_name = "event_detail"
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        res_obj = {}
        try:
            req_obj = request.json
            trim_object(req_obj)
            res_obj = event_detail(req_obj, config_obj)
        except Exception as e:
            log_path = current_app.config["LOG_PATH"]
            res_obj = get_error_obj(api_name, traceback.format_exc(), log_path)
        return res_obj


    @api.doc(False)
    def get(self):
        return self.post()


@api.route('/list/')
class Event(Resource):
    @api.doc('list')
    @api.expect(list_query_model)
    def post(self):
        api_name = "event_list"
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        res_obj = {}
        try:
            req_obj = request.json
            trim_object(req_obj)
            res_obj = event_list(req_obj, config_obj)
        except Exception as e:
            log_path = current_app.config["LOG_PATH"]
            res_obj = get_error_obj(api_name, traceback.format_exc(), log_path)
        return res_obj

    @api.doc(False)
    def get(self):
        return self.post()


@api.route('/update/')
class Event(Resource):
    @api.doc('update')
    @api.expect(update_query_model)
    #@jwt_required
    def post(self):
        api_name = "event_update"
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
            res_obj = event_update(current_user, req_obj, config_obj)
        except Exception as e:
            log_path = current_app.config["LOG_PATH"]
            res_obj = get_error_obj(api_name, traceback.format_exc(), log_path)
        return res_obj

    @api.doc(False)
    def get(self):
        return self.post()



@api.route('/delete/')
class Event(Resource):
    @api.doc('delete')
    @api.expect(delete_query_model)
    #@jwt_required
    def post(self):
        api_name = "event_delete"
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
            res_obj = event_delete(current_user, req_obj, config_obj)
        except Exception as e:
            log_path = current_app.config["LOG_PATH"]
            res_obj = get_error_obj(api_name, traceback.format_exc(), log_path)
        return res_obj

    
    @api.doc(False)
    def get(self):
        return self.post()




