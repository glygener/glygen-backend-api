import os,sys
from flask_restx import Namespace, Resource, fields
from flask import (request, current_app, session, jsonify)

from glygen.db import get_mongodb
from glygen.document import get_one, get_many, insert_one, update_one, delete_one, order_json_obj
from werkzeug.utils import secure_filename
import datetime
import time
import subprocess
import json
import bcrypt

from flask_jwt_extended import (
    jwt_required, create_access_token,
    create_refresh_token,
    get_jwt_identity, set_access_cookies, get_csrf_token,
    set_refresh_cookies, unset_jwt_cookies
    )

from glygen.auth_apilib import auth_userid, auth_contact, auth_register, auth_login,  auth_userinfo, auth_userupdate, auth_userdelete, auth_contactlist, auth_contactupdate, auth_contactdelete

from glygen.util import get_error_obj, trim_object
import traceback



api = Namespace("auth", description="Auth APIs")
userid_query_model = api.model('Yyy Query',{ 'query':fields.String(required=True, default="", description="")})
contact_query_model = api.model('Yyy Query',{ 'query':fields.String(required=True, default="", description="")})
register_query_model = api.model('Yyy Query',{ 'query':fields.String(required=True, default="", description="")})
login_query_model = api.model('Login Query',{ 'query':fields.String(required=True, default="", description="")})
userinfo_query_model = api.model('Yyy Query',{ 'query':fields.String(required=True, default="", description="")})
userupdate_query_model = api.model('User Update Query',{ 'query':fields.String(required=True, default="", description="")})
userdelete_query_model = api.model('User Delete Query',{ 'query':fields.String(required=True,    default="", description="")})

contactlist_query_model = api.model('Yyy Query',{ 'query':fields.String(required=True, default="", description="")})
contactupdate_query_model = api.model('Yyy Query',{ 'query':fields.String(required=True, default="", description="")})
contactdelete_query_model = api.model('Yyy Query',{ 'query':fields.String(required=True, default="", description="")})






@api.route('/userid/')
class Auth(Resource):
    @api.doc('userid')
    @api.expect(userid_query_model)
    def post(self):
        api_name = "auth_userid"
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        res_obj = {}
        try:
            req_obj = request.json
            trim_object(req_obj)
            res_obj = auth_userid(config_obj)
        except Exception as e:
            log_path = current_app.config["LOG_PATH"]
            res_obj = get_error_obj(api_name, traceback.format_exc(), log_path)
        http_code = 500 if "error_list" in res_obj else 200
        return res_obj


@api.route('/contact/')
class Auth(Resource):
    @api.doc('contact')
    @api.expect(contact_query_model)
    def post(self):
        api_name = "auth_contact"
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        res_obj = {}
        try:
            req_obj = request.json
            trim_object(req_obj)
            res_obj = auth_contact(req_obj, config_obj)
        except Exception as e:
            log_path = current_app.config["LOG_PATH"]
            res_obj = get_error_obj(api_name, traceback.format_exc(), log_path)
        http_code = 500 if "error_list" in res_obj else 200
        return res_obj


@api.route('/register/')
class Auth(Resource):
    @api.doc('register')
    @api.expect(register_query_model)
    def post(self):
        api_name = "auth_register"
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        res_obj = {}
        try:
            req_obj = request.json
            #req_obj["status"], req_obj["access"], req_obj["role"] = 1, "write", "admin"
            req_obj["status"], req_obj["access"], req_obj["role"] = 0, "readonly", ""

            trim_object(req_obj)
            res_obj = auth_register(req_obj, config_obj)
        except Exception as e:
            log_path = current_app.config["LOG_PATH"]
            res_obj = get_error_obj(api_name, traceback.format_exc(), log_path)
        http_code = 500 if "error_list" in res_obj else 200
        return res_obj



@api.route('/login/')
class Auth(Resource):
    @api.doc('login')
    @api.expect(login_query_model)
    def post(self):
        api_name = "auth_login"
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        res_obj = {}
        try:
            req_obj = request.json
            trim_object(req_obj)
            username = req_obj["email"]
            password = req_obj["password"]
            mongo_dbh, error_obj = get_mongodb()
            if error_obj != {}:
                return error_obj, 500
            user_doc = mongo_dbh["c_users"].find_one({'email' : username })
            error = None
            if user_doc is None:
                error = "incorrect-email/password"
            else:
                submitted_password = password.encode('utf-8')
                #stored_password = user_doc['password'].encode('utf-8')
                stored_password = user_doc['password']
                if bcrypt.hashpw(submitted_password, stored_password) != stored_password:
                    error = "incorrect-email/password"
            res_obj = {"status":1}
            if error is None:
                access_token = create_access_token(identity=username, expires_delta=None)
                refresh_token = create_refresh_token(identity=username)
                res_obj["access_token"] = access_token
                res_obj["access_csrf"] = get_csrf_token(access_token)
                res_obj["refresh_csrf"] = get_csrf_token(refresh_token)
                res_obj["username"] = user_doc["email"]
                #res_obj["fullname"] = user_doc["fname"] + " " + user_doc["lname"]
                session['email'] = user_doc["email"]
                res_obj = jsonify(res_obj)
                set_access_cookies(res_obj, access_token)
                set_refresh_cookies(res_obj, refresh_token)
            else:
                res_obj = {"error_list":[{"error_code":error}]}
        except Exception as e:
            log_path = current_app.config["LOG_PATH"]
            res_obj = get_error_obj(api_name, traceback.format_exc(), log_path)
            
        #http_code = 500 if "error_list" in res_obj else 200
        return res_obj






@api.route('/userinfo/')
class Auth(Resource):
    @api.doc('userinfo')
    @api.expect(userinfo_query_model)
    #@jwt_required
    def post(self):
        api_name = "auth_userinfo"
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
            res_obj = auth_userinfo(current_user, req_obj, config_obj)
        except Exception as e:
            log_path = current_app.config["LOG_PATH"]
            res_obj = get_error_obj(api_name, traceback.format_exc(), log_path)
        http_code = 500 if "error_list" in res_obj else 200
        return res_obj



@api.route('/userupdate/')
class Auth(Resource):
    @api.doc('userupdate')
    @api.expect(userupdate_query_model)
    #@jwt_required
    def post(self):
        api_name = "auth_userupdate"
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
            res_obj = auth_userupdate(current_user, req_obj, config_obj)
        except Exception as e:
            log_path = current_app.config["LOG_PATH"]
            res_obj = get_error_obj(api_name, traceback.format_exc(), log_path)
        http_code = 500 if "error_list" in res_obj else 200
        
        return res_obj

@api.route('/userdelete/')
class Auth(Resource):
    @api.doc('userdelete')
    @api.expect(userdelete_query_model)
    #@jwt_required
    def post(self):
        api_name = "auth_userdelete"
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
            res_obj = auth_userdelete(current_user, req_obj, config_obj)
        except Exception as e:
            log_path = current_app.config["LOG_PATH"]
            res_obj = get_error_obj(api_name, traceback.format_exc(), log_path)
        http_code = 500 if "error_list" in res_obj else 200

        return res_obj



@api.route('/contactlist/')
class Auth(Resource):
    @api.doc('contactlist')
    @api.expect(contactlist_query_model)
    #@jwt_required
    def post(self):
        api_name = "auth_contactlist"
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
            res_obj = auth_contactlist(current_user, req_obj, config_obj)
        except Exception as e:
            log_path = current_app.config["LOG_PATH"]
            res_obj = get_error_obj(api_name, traceback.format_exc(), log_path)
        http_code = 500 if "error_list" in res_obj else 200
        return res_obj


@api.route('/contactupdate/')
class Auth(Resource):
    @api.doc('contactupdate')
    @api.expect(contactupdate_query_model)
    #@jwt_required
    def post(self):
        api_name = "auth_contactupdate"
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
            res_obj = auth_contactupdate(current_user, req_obj, config_obj)
        except Exception as e:
            log_path = current_app.config["LOG_PATH"]
            res_obj = get_error_obj(api_name, traceback.format_exc(), log_path)
        http_code = 500 if "error_list" in res_obj else 200
        return res_obj


@api.route('/contactdelete/')
class Auth(Resource):
    @api.doc('contactdelete')
    @api.expect(contactdelete_query_model)
    #@jwt_required
    def post(self):
        api_name = "auth_contactdelete"
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
            res_obj = auth_contactdelete(current_user, req_obj, config_obj)
        except Exception as e:
            log_path = current_app.config["LOG_PATH"]
            res_obj = get_error_obj(api_name, traceback.format_exc(), log_path)
        http_code = 500 if "error_list" in res_obj else 200
        return res_obj








