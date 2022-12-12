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

from glygen.job_apilib import job_addnew, job_detail, job_update, job_list, job_delete,job_clean, job_results, job_status, job_queue, job_init

from glygen.util import get_error_obj, trim_object
import traceback




api = Namespace("job", description="Job APIs")

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
clean_query_model = api.model(
    'Clean Query', { 'query': fields.String(required=True, default="", description='')})
results_query_model = api.model(
    'Results Query', { 'query': fields.String(required=True, default="", description='')})
status_query_model = api.model(
    'Status Query', { 'query': fields.String(required=True, default="", description='')})
queue_query_model = api.model(
    'Queue Query', { 'query': fields.String(required=True, default="", description='')})
init_query_model = api.model(
    'Init Query', { 'query': fields.String(required=True, default="", description='')})



@api.route('/init/')
class Job(Resource):
    @api.doc('init')
    @api.expect(init_query_model)
    def post(self):
        api_name = "job_init"
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        config_obj["server"] = os.environ["SERVER"]
        res_obj = {}
        try:
            req_obj = request.json
            trim_object(req_obj)
            res_obj = job_init(config_obj, os.environ["DATA_PATH"])
        except Exception as e:
            log_path = current_app.config["LOG_PATH"]
            res_obj = get_error_obj(api_name, traceback.format_exc(), log_path)
        return res_obj



@api.route('/addnew/')
class Job(Resource):
    @api.doc('addnew')
    @api.expect(addnew_query_model)
    def post(self):
        api_name = "job_addnew"
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        config_obj["server"] = os.environ["SERVER"]
        res_obj = {}
        try:
            req_obj = request.json
            trim_object(req_obj)
            data_path, server = os.environ["DATA_PATH"],os.environ["SERVER"]
            res_obj = job_addnew(req_obj, config_obj, data_path, server)
        except Exception as e:
            log_path = current_app.config["LOG_PATH"] 
            res_obj = get_error_obj(api_name, traceback.format_exc(), log_path)
        return res_obj

@api.route('/detail/')
class Job(Resource):
    @api.doc('detail')
    @api.expect(detail_query_model)
    def post(self):
        api_name = "job_detail"
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        config_obj["server"] = os.environ["SERVER"]
        res_obj = {}
        try:
            req_obj = request.json
            trim_object(req_obj)
            res_obj = job_detail(req_obj, config_obj)
        except Exception as e:
            log_path = current_app.config["LOG_PATH"]
            res_obj = get_error_obj(api_name, traceback.format_exc(), log_path)
        return res_obj


@api.route('/list/')
class Job(Resource):
    @api.doc('list')
    @api.expect(list_query_model)
    def post(self):
        api_name = "job_list"
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        config_obj["server"] = os.environ["SERVER"]
        res_obj = {}
        try:
            req_obj = request.json
            trim_object(req_obj)
            res_obj = job_list(req_obj, config_obj)
        except Exception as e:
            log_path = current_app.config["LOG_PATH"]
            res_obj = get_error_obj(api_name, traceback.format_exc(), log_path)
        return res_obj

@api.route('/update/')
class Job(Resource):
    @api.doc('update')
    @api.expect(update_query_model)
    def post(self):
        api_name = "job_update"
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        config_obj["server"] = os.environ["SERVER"]
        res_obj = {}
        try:
            req_obj = request.json
            trim_object(req_obj)
            res_obj = job_update(req_obj, config_obj)
        except Exception as e:
            log_path = current_app.config["LOG_PATH"]
            res_obj = get_error_obj(api_name, traceback.format_exc(), log_path)
        return res_obj


@api.route('/delete/')
class Job(Resource):
    @api.doc('delete')
    @api.expect(delete_query_model)
    def post(self):
        api_name = "job_delete"
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        config_obj["server"] = os.environ["SERVER"]
        res_obj = {}
        try:
            req_obj = request.json
            trim_object(req_obj)
            res_obj = job_delete(req_obj, config_obj)
        except Exception as e:
            log_path = current_app.config["LOG_PATH"]
            res_obj = get_error_obj(api_name, traceback.format_exc(), log_path)
        return res_obj



@api.route('/results/')
class Job(Resource):
    @api.doc('results')
    @api.expect(results_query_model)
    def post(self):
        api_name = "job_results"
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        config_obj["server"] = os.environ["SERVER"]
        res_obj = {}
        try:
            req_obj = request.json
            trim_object(req_obj)
            res_obj = job_results(req_obj, config_obj)
        except Exception as e:
            log_path = current_app.config["LOG_PATH"]
            res_obj = get_error_obj(api_name, traceback.format_exc(), log_path)
        return res_obj

@api.route('/status/')
class Job(Resource):
    @api.doc('status')
    @api.expect(status_query_model)
    def post(self):
        api_name = "job_status"
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        config_obj["server"] = os.environ["SERVER"]
        res_obj = {}
        try:
            req_obj = request.json
            trim_object(req_obj)
            res_obj = job_status(req_obj, config_obj)
        except Exception as e:
            log_path = current_app.config["LOG_PATH"]
            res_obj = get_error_obj(api_name, traceback.format_exc(), log_path)
        return res_obj

@api.route('/queue/')
class Job(Resource):
    @api.doc('queue')
    @api.expect(queue_query_model)
    def post(self):
        api_name = "job_queue"
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        config_obj["server"] = os.environ["SERVER"]
        res_obj = {}
        try:
            req_obj = request.json
            trim_object(req_obj)
            res_obj = job_queue(req_obj, config_obj)
        except Exception as e:
            log_path = current_app.config["LOG_PATH"]
            res_obj = get_error_obj(api_name, traceback.format_exc(), log_path)
        return res_obj


@api.route('/clean/')
class Job(Resource):
    @api.doc('clean')
    @api.expect(clean_query_model)
    def post(self):
        api_name = "job_clean"
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        config_obj["server"] = os.environ["SERVER"]
        res_obj = {}
        try:
            data_path, server = os.environ["DATA_PATH"],os.environ["SERVER"]
            res_obj = job_clean(data_path, server)
        except Exception as e:
            log_path = current_app.config["LOG_PATH"]
            res_obj = get_error_obj(api_name, traceback.format_exc(), log_path)
        return res_obj



