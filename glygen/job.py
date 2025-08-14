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

from glygen.job_apilib import job_addnew, job_detail, job_update, job_list, job_delete,job_clean, job_results, job_status, job_queue, job_init, job_status_many

from glygen.util import get_req_obj, validate_uploaded_table
import traceback




api = Namespace("job", description="Job APIs")

PARAMS = api.model(
    "PARAMS",
    {
        "seq":fields.String(required=True, default="MSIQENISSLQLRSWVSKSQRDLAKSILIGAPGGPAGYLRRASVAQLTQELGTAFFQQQQLPAAMADTFLEHLCLLDIDSEPVAARSTSIIATIGPASRSVERLKEMIKAGMNIARLNFSQHAIAREAEAAVYHRQLFEELRRAAPLSRDPTEVTAIGAVEAAFKCCAAAIIVLTTT"),
        "targetdb":fields.String(required=True, default="canonicalsequences_all"),
        "num_alignments":fields.Integer(required=True, default=3),
        "evalue":fields.Float(required=True, default=1e-3)
    }
)

addnew_query_model = api.model(
    'Job Addnew Query', 
    { 
        "jobtype":fields.String(required=True, default="blastp"),
        "parameters":fields.Nested(PARAMS)
    }
)
detail_query_model = api.model(
    'Job Detail Query', 
    { 'jobid': fields.Integer(required=True, default=1)}
)

list_query_model = api.model(
    'Job List Query', 
    {
        "visibility":fields.String(required=True, default="all")
    }
)
update_query_model = api.model(
    'Job Update Query', 
    {
    }
)
delete_query_model = api.model(
    'Job Delete Query', 
    { 'jobid': fields.Integer(required=True, default=1)}
)   
results_query_model = api.model(
    'Job Results Query', 
    { 'jobid': fields.Integer(required=True, default=1)}
)

status_query_model = api.model(
    'Job Status Query',
    { 'jobid': fields.Integer(required=True, default=1)}
)   
status_many_query_model = api.model(
    'Job Status Many Query',
    {"jobidlist":fields.List(fields.Integer(), required=True, default=[])}
)



clean_query_model = api.model('Job Clean Query', {})
queue_query_model = api.model('Job Queue Query', {})
init_query_model = api.model('Job Init Query', {})



@api.route('/init/')
class Job(Resource):
    @api.expect(init_query_model)
    def post(self):
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        config_obj["server"] = os.environ["SERVER"]
        json_url = os.path.join(SITE_ROOT, "conf/job_init.json")
        config_obj["job_init"] = json.load(open(json_url))

        res_obj = {}
        try:
            req_obj = get_req_obj(request)
            res_obj = log_request(req_obj, "/job/init/", request)
            if "error_list" not in res_obj:
                res_obj = job_init(config_obj, os.environ["DATA_PATH"])
        except Exception as e:
            res_obj = log_error(traceback.format_exc())
        http_code = 500 if "error_list" in res_obj else 200
        return res_obj, http_code

    @api.doc(False)
    def get(self):
        return self.post()


@api.route('/addnew/', methods=['GET', 'POST'])
class Job(Resource):
    @api.expect(addnew_query_model)
    def post(self):
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        config_obj["server"] = os.environ["SERVER"]
        res_obj = {}
        try:
            req_obj_form = request.form
            req_obj_json = request.json
            req_obj = {}
            if req_obj_json != None:
                req_obj = req_obj_json
            else:
                for k in req_obj_form:
                    req_obj[k] = req_obj_form[k]
                req_obj["parameters"] = {}
                req_obj["intable"] = [["isoform_ac","amino_acid_pos","amino_acid"]]
                if "userfile" in request.files:
                    file_buffer = request.files.get("userfile").read()
                    file_size = len(file_buffer)
                    max_size = 50000000
                    if file_size > max_size:
                        res_obj = {
                            "error_list":[{"error_code":"file-size-exceeds-%sBytes" % (max_size) }],
                            "result_count":0
                        }
                        return res_obj, 200
                    file_buffer = file_buffer.decode()
                    file_buffer = file_buffer.replace("\r", "\n").replace("\n\n", "\n")
                    line_list = file_buffer.split("\n")
                    for line in line_list[1:]:
                        if line.strip() == "":
                            continue
                        row = []
                        for val in line.strip().split(","):
                            row.append(val.replace("\"", ""))
                        req_obj["intable"].append(row)
                    validation_res = validate_uploaded_table(req_obj["intable"], "isoform_mapper")
                    if "error_list" in validation_res:
                        return validation_res, 200
            if req_obj["jobtype"] == "isoform_mapper":
                if "intable" in req_obj:
                    max_row_count = 1000
                    if len(req_obj["intable"]) - 1 > max_row_count:
                        res_obj = {
                            "error_list":[{"error_code":"row-count-exceeds-%s" % (max_row_count) }],
                            "result_count":0
                        }
                        return res_obj, 200

            qry = req_obj["query"] if "query" in req_obj else req_obj
            data_path, server = os.environ["DATA_PATH"],os.environ["SERVER"]
            tmp_req_obj = json.loads(json.dumps(req_obj))
            res_obj = log_request(tmp_req_obj, "/job/addnew/", request)
            if "error_list" not in res_obj:
                res_obj = job_addnew(qry, config_obj, data_path, server)
        except Exception as e:
            res_obj = log_error(traceback.format_exc())
        
        http_code = 200
        http_code = 500 if "error_list" in res_obj and "result_count" not in res_obj else http_code
        return res_obj, http_code
    
    @api.doc(False)
    def get(self):
        return self.post()

@api.route('/detail/')
class Job(Resource):
    @api.expect(detail_query_model)
    def post(self):
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        config_obj["server"] = os.environ["SERVER"]
        res_obj = {}
        try:
            req_obj = get_req_obj(request)
            res_obj = log_request(req_obj, "/job/detail/", request)
            if "error_list" not in res_obj:
                res_obj = job_detail(req_obj, config_obj)
        except Exception as e:
            res_obj = log_error(traceback.format_exc())
        http_code = 500 if "error_list" in res_obj else 200
        return res_obj, http_code

    @api.doc(False)
    def get(self):
        return self.post()

@api.route('/list/')
class Job(Resource):
    @api.expect(list_query_model)
    def post(self):
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        config_obj["server"] = os.environ["SERVER"]
        res_obj = {}
        try:
            req_obj = get_req_obj(request)
            res_obj = log_request(req_obj, "/job/list/", request)
            if "error_list" not in res_obj:
                res_obj = job_list(req_obj, config_obj)
        except Exception as e:
            res_obj = log_error(traceback.format_exc())
        
        http_code = 500 if "error_list" in res_obj else 200
        return res_obj, http_code
        
    @api.doc(False)
    def get(self):
        return self.post()

@api.route('/update/')
class Job(Resource):
    @api.doc(False)
    @api.expect(update_query_model)
    def post(self):
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        config_obj["server"] = os.environ["SERVER"]
        res_obj = {}
        try:
            req_obj = get_req_obj(request)
            res_obj = log_request(req_obj, "/job/update/", request)
            if "error_list" not in res_obj:
                res_obj = job_update(req_obj, config_obj)
        except Exception as e:
            res_obj = log_error(traceback.format_exc())
        http_code = 500 if "error_list" in res_obj else 200
        return res_obj, http_code

    @api.doc(False)
    def get(self):
        return self.post()


@api.route('/delete/')
class Job(Resource):
    @api.expect(delete_query_model)
    def post(self):
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        config_obj["server"] = os.environ["SERVER"]
        res_obj = {}
        try:
            req_obj = get_req_obj(request)
            res_obj = log_request(req_obj, "/job/delete/", request)
            if "error_list" not in res_obj:
                res_obj = job_delete(req_obj, config_obj)
        except Exception as e:
            res_obj = log_error(traceback.format_exc())
        http_code = 500 if "error_list" in res_obj else 200
        return res_obj, http_code

    @api.doc(False)
    def get(self):
        return self.post()


@api.route('/results/')
class Job(Resource):
    @api.expect(results_query_model)
    def post(self):
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        config_obj["server"] = os.environ["SERVER"]
        res_obj = {}
        try:
            req_obj = get_req_obj(request)
            res_obj = log_request(req_obj, "/job/results/", request)
            if "error_list" not in res_obj:
                res_obj = job_results(req_obj, config_obj)
        except Exception as e:
            res_obj = log_error(traceback.format_exc())
        
        http_code = 500 if "error_list" in res_obj else 200
        return res_obj, http_code

    @api.doc(False)
    def get(self):
        return self.post()

@api.route('/status/')
class Job(Resource):
    @api.expect(status_query_model)
    def post(self):
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        config_obj["server"] = os.environ["SERVER"]
        res_obj = {}
        try:
            req_obj = get_req_obj(request)
            res_obj = log_request(req_obj, "/job/status/", request)
            if "error_list" not in res_obj:
                res_obj = job_status(req_obj, config_obj)
        except Exception as e:
            res_obj = log_error(traceback.format_exc())
        
        http_code = 500 if "error_list" in res_obj else 200
        return res_obj, http_code

    @api.doc(False)
    def get(self):
        return self.post()

@api.route('/status_many/')
class Job(Resource):
    @api.expect(status_many_query_model)
    def post(self):
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        config_obj["server"] = os.environ["SERVER"]
        res_obj = {}
        try:
            req_obj = get_req_obj(request)
            res_obj = log_request(req_obj, "/job/status_many/", request)
            if "error_list" not in res_obj:
                res_obj = job_status_many(req_obj, config_obj)
        except Exception as e:
            res_obj = log_error(traceback.format_exc())

        http_code = 500 if "error_list" in res_obj else 200
        return res_obj, http_code

    @api.doc(False)
    def get(self):
        return self.post()



@api.route('/queue/')
class Job(Resource):
    @api.expect(queue_query_model)
    def post(self):
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        config_obj["server"] = os.environ["SERVER"]
        res_obj = {}
        try:
            req_obj = get_req_obj(request)
            res_obj = log_request(req_obj, "/job/queue/", request)
            if "error_list" not in res_obj:
                res_obj = job_queue(req_obj, config_obj)
        except Exception as e:
            res_obj = log_error(traceback.format_exc())
        
        http_code = 500 if "error_list" in res_obj else 200
        return res_obj, http_code

    @api.doc(False)
    def get(self):
        return self.post()


@api.route('/clean/')
class Job(Resource):
    @api.doc(False)
    @api.expect(clean_query_model)
    def post(self):
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        config_obj["server"] = os.environ["SERVER"]
        res_obj = {}
        try:
            data_path, server = os.environ["DATA_PATH"],os.environ["SERVER"]
            res_obj = log_request({}, "/job/clean/", request)
            if "error_list" not in res_obj:
                res_obj = job_clean(data_path, server)
        except Exception as e:
            res_obj = log_error(traceback.format_exc())
        
        http_code = 500 if "error_list" in res_obj else 200
        return res_obj, http_code

    @api.doc(False)
    def get(self):
        return self.post()


