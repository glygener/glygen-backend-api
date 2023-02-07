import os,sys
from flask_restx import Namespace, Resource, fields
from flask import (request, current_app, session, jsonify)
from glygen.db import get_mongodb, log_error
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

from glygen.util import get_req_obj
import traceback



api = Namespace("auth", description="Auth APIs")


register_query_model = api.model("Auth Register Query",
    { 
        "email":fields.String(required=True, default=""),
        "password":fields.String(required=True, default="")
    }
)
login_query_model = api.model("Auth Login Query",
    { 
        "email":fields.String(required=True, default=""),
        "password":fields.String(required=True, default="")
    }
)
userid_query_model = api.model("Auth UserID Query",{})
userinfo_query_model = api.model("Auth User Info Query",
    { 
        "email":fields.String(required=True, default="")
    }
)
contactlist_query_model = api.model("Auth Contact List Query",
    { 
        "visibility":fields.String(required=True, default="all")
    }
)
contactupdate_query_model = api.model("Auth Contact Update Query",
    { 
        "id":fields.String(required=True, default="")
    }
)
contactdelete_query_model = api.model("Auth Contact Delete Query",
    { 
        "id":fields.String(required=True, default="")
    }
)
contact_query_model = api.model("Auth Contact Query",
    {
        "fname":fields.String(required=True, default=""),
        "lname":fields.String(required=True, default=""),
        "email":fields.String(required=True, default=""),
        "subject":fields.String(required=True, default=""),
        "message":fields.String(required=True, default="")
    }
)



@api.route('/userid/')
class Auth(Resource):
    @api.expect(userid_query_model)
    def post(self):
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        res_obj = {}
        try:
            req_obj = get_req_obj(request)
            res_obj = auth_userid(config_obj)
        except Exception as e:
            res_obj =  log_error(traceback.format_exc())
        http_code = 500 if "error_list" in res_obj else 200
        return res_obj, http_code

    @api.doc(False)
    def get(self):
        return self.post()

@api.route('/contact/')
class Auth(Resource):
    @api.expect(contact_query_model)
    def post(self):
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        res_obj = {}
        try:
            req_obj = get_req_obj(request)
            res_obj = auth_contact(req_obj, config_obj)
        except Exception as e:
            res_obj =  log_error(traceback.format_exc())
        http_code = 500 if "error_list" in res_obj else 200
        return res_obj, http_code

    @api.doc(False)
    def get(self):
        return self.post()


@api.route('/register/')
class Auth(Resource):
    @api.expect(register_query_model)
    def post(self):
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        res_obj = {}
        try:
            req_obj = get_req_obj(request)
            req_obj["status"], req_obj["access"], req_obj["role"] = 0, "readonly", ""
            if req_obj["email"] in config_obj["admin_list"]:
                req_obj["status"], req_obj["access"], req_obj["role"] = 1, "write", "admin"
            res_obj = auth_register(req_obj, config_obj)
        except Exception as e:
            res_obj =  log_error(traceback.format_exc())
        http_code = 500 if "error_list" in res_obj else 200
        return res_obj, http_code

    @api.doc(False)
    def get(self):
        return self.post()


@api.route('/login/')
class Auth(Resource):
    @api.expect(login_query_model)
    def post(self):
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        res_obj = {}
        try:
            req_obj = get_req_obj(request)
            username = req_obj["email"]
            password = req_obj["password"]
            mongo_dbh, error_obj = get_mongodb()
            if error_obj != {}:
                return error_obj, 500
            user_doc = mongo_dbh["c_users"].find_one({'email' : username })
            error = None
            if user_doc is None:
                error = "incorrect-email/password"
            elif "password" not in user_doc:
                error = "password does not exist for registerd user"
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
                session['email'] = user_doc["email"]
                res_obj = jsonify(res_obj)
                set_access_cookies(res_obj, access_token)
                set_refresh_cookies(res_obj, refresh_token)
            else:
                res_obj = {"error_list":[{"error_code":error}]}
        except Exception as e:
            res_obj =  log_error(traceback.format_exc())
        http_code = 500 if "error_list" in res_obj else 200
        return res_obj, http_code

    @api.doc(False)
    def get(self):
        return self.post()





@api.route('/userinfo/')
class Auth(Resource):
    @api.doc(False)
    @api.expect(userinfo_query_model)
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
            res_obj = auth_userinfo(current_user, req_obj, config_obj)
        except Exception as e:
            res_obj =  log_error(traceback.format_exc())
        http_code = 500 if "error_list" in res_obj else 200
        return res_obj, http_code

    @api.doc(False)
    def get(self):
        return self.post()


@api.route('/userupdate/')
class Auth(Resource):
    @api.doc(False)
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
            res_obj = auth_userupdate(current_user, req_obj, config_obj)
        except Exception as e:
            res_obj =  log_error(traceback.format_exc())
        
        http_code = 500 if "error_list" in res_obj else 200
        return res_obj, http_code

    @api.doc(False)
    def get(self):
        return self.post()

@api.route('/userdelete/')
class Auth(Resource):
    @api.doc(False)
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
            res_obj = auth_userdelete(current_user, req_obj, config_obj)
        except Exception as e:
            res_obj =  log_error(traceback.format_exc())
        http_code = 500 if "error_list" in res_obj else 200
        return res_obj, http_code

    @api.doc(False)
    def get(self):
        return self.post()


@api.route('/contactlist/')
class Auth(Resource):
    @api.doc(False)
    @api.expect(contactlist_query_model)
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
            res_obj = auth_contactlist(current_user, req_obj, config_obj)
        except Exception as e:
            res_obj =  log_error(traceback.format_exc())
        http_code = 500 if "error_list" in res_obj else 200
        return res_obj, http_code

    @api.doc(False)
    def get(self):
        return self.post()

@api.route('/contactupdate/')
class Auth(Resource):
    @api.doc(False)
    @api.expect(contactupdate_query_model)
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
            res_obj = auth_contactupdate(current_user, req_obj, config_obj)
        except Exception as e:
            res_obj =  log_error(traceback.format_exc())
        http_code = 500 if "error_list" in res_obj else 200
        return res_obj, http_code

    @api.doc(False)
    def get(self):
        return self.post()

@api.route('/contactdelete/')
class Auth(Resource):
    @api.doc(False)
    @api.expect(contactdelete_query_model)
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
            res_obj = auth_contactdelete(current_user, req_obj, config_obj)
        except Exception as e:
            res_obj =  log_error(traceback.format_exc())
        http_code = 500 if "error_list" in res_obj else 200
        return res_obj, http_code

    @api.doc(False)
    def get(self):
        return self.post()






