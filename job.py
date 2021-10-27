import os
import json
import string
import csv
import cgi
import traceback
import job_apilib as apilib
import errorlib
import util

from flask import Flask, request, jsonify, render_template, send_file
from flask_cors import CORS
app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False
CORS(app)


global config_obj
global path_obj

config_obj = json.loads(open("./conf/config.json", "r").read())
path_obj  =  config_obj[config_obj["server"]]["pathinfo"]



@app.route('/job/init/', methods=['GET', 'POST'])
def job_init():
  
    res_obj = {}
    try:
        res_obj = apilib.job_init(config_obj)
    except Exception, e:
        res_obj = errorlib.get_error_obj("job_init", traceback.format_exc(), path_obj)
    
    http_code = 500 if "error_list" in res_obj else 200
    return jsonify(res_obj), http_code



@app.route('/job/addnew/', methods=['GET', 'POST'])
def job_addnew():

    query_obj = {}
    query_obj["line_list"] = []
    form_dict = cgi.FieldStorage()
    for f in form_dict:
        if f != "userfile":
             query_obj[f] = form_dict[f].value

    if "userfile" in form_dict:
        file_buffer = form_dict["userfile"].file.read()
        file_buffer = file_buffer.replace("\r", "\n")
        file_buffer = file_buffer.replace("\n\n", "\n")
        query_obj["line_list"] += file_buffer.split("\n")

    if "pasted_text" in form_dict:
        if form_dict["pasted_text"].value.strip() != "":
            for line in form_dict["pasted_text"].value.split("\n"):
                query_obj["line_list"].append(line)

    res_obj = {}
    try:
        res_obj = apilib.job_addnew(query_obj, config_obj)
    except Exception, e:
        res_obj = errorlib.get_error_obj("job_addnew", traceback.format_exc(), path_obj)


    http_code = 500 if "error_list" in res_obj else 200
    return jsonify(res_obj), http_code


@app.route('/job/status/', methods=['GET', 'POST'])
def job_status():

    res_obj = {}
    try:
        query_value = util.get_arg_value("query", request.method)
        if query_value == "":
            res_obj = {"error_list":[{"error_code": "missing-query-key-in-query-json"}]}
        elif util.is_valid_json(query_value) == False:
            res_obj = {"error_list":[{"error_code": "invalid-query-json"}]}
        else:
            query_obj = json.loads(query_value)
            util.trim_object(query_obj)
            res_obj = apilib.job_status(query_obj, config_obj)
    except Exception, e:
        res_obj = errorlib.get_error_obj("job_status", traceback.format_exc(), path_obj)

    http_code = 500 if "error_list" in res_obj else 200
    return jsonify(res_obj), http_code


@app.route('/job/queue/', methods=['GET', 'POST'])
def job_queue():

    res_obj = {}
    try:
        query_value = util.get_arg_value("query", request.method)
        if query_value == "":
            res_obj = {"error_list":[{"error_code": "missing-query-key-in-query-json"}]}
        elif util.is_valid_json(query_value) == False:
            res_obj = {"error_list":[{"error_code": "invalid-query-json"}]}
        else:
            query_obj = json.loads(query_value)
            util.trim_object(query_obj)
            res_obj = apilib.job_queue(query_obj, config_obj)
    except Exception, e:
        res_obj = errorlib.get_error_obj("job_queue", traceback.format_exc(), path_obj)

    http_code = 500 if "error_list" in res_obj else 200
    return jsonify(res_obj), http_code



@app.route('/job/update/', methods=['GET', 'POST'])
def job_update():

    res_obj = {}
    try:
        query_value = util.get_arg_value("query", request.method)
        if query_value == "":
            res_obj = {"error_list":[{"error_code": "missing-query-key-in-query-json"}]}
        elif util.is_valid_json(query_value) == False:
            res_obj = {"error_list":[{"error_code": "invalid-query-json"}]}
        else:
            query_obj = json.loads(query_value)
            util.trim_object(query_obj)
            res_obj = apilib.job_update(query_obj, config_obj)
    except Exception, e:
        res_obj = errorlib.get_error_obj("job_update", traceback.format_exc(), path_obj)

    http_code = 500 if "error_list" in res_obj else 200
    return jsonify(res_obj), http_code


@app.route('/job/detail/', methods=['GET', 'POST'])
def job_detail():

    res_obj = {}
    try:
        query_value = util.get_arg_value("query", request.method)
        if query_value == "":
            res_obj = {"error_list":[{"error_code": "missing-query-key-in-query-json"}]}
        elif util.is_valid_json(query_value) == False:
            res_obj = {"error_list":[{"error_code": "invalid-query-json"}]}
        else:
            query_obj = json.loads(query_value)
            util.trim_object(query_obj)
            res_obj = apilib.job_detail(query_obj, config_obj)
    except Exception, e:
        res_obj = errorlib.get_error_obj("job_detail", traceback.format_exc(), path_obj)

    http_code = 500 if "error_list" in res_obj else 200
    return jsonify(res_obj), http_code


@app.route('/job/list/', methods=['GET', 'POST'])
def job_list():

    res_obj = {}
    try:
        query_value = util.get_arg_value("query", request.method)
        if query_value == "":
            res_obj = {"error_list":[{"error_code": "missing-query-key-in-query-json"}]}
        elif util.is_valid_json(query_value) == False:
            res_obj = {"error_list":[{"error_code": "invalid-query-json"}]}
        else:
            query_obj = json.loads(query_value)
            util.trim_object(query_obj)
            res_obj = apilib.job_list(query_obj, config_obj)
    except Exception, e:
        res_obj = errorlib.get_error_obj("job_list", traceback.format_exc(), path_obj)

    http_code = 500 if "error_list" in res_obj else 200
    return jsonify(res_obj), http_code



@app.route('/job/delete/', methods=['GET', 'POST'])
def job_delete():

    res_obj = {}
    try:
        query_value = util.get_arg_value("query", request.method)
        if query_value == "":
            res_obj = {"error_list":[{"error_code": "missing-query-key-in-query-json"}]}
        elif util.is_valid_json(query_value) == False:
            res_obj = {"error_list":[{"error_code": "invalid-query-json"}]}
        else:
            query_obj = json.loads(query_value)
            util.trim_object(query_obj)
            res_obj = apilib.job_delete(query_obj, config_obj)
    except Exception, e:
        res_obj = errorlib.get_error_obj("job_delete", traceback.format_exc(), path_obj)

    http_code = 500 if "error_list" in res_obj else 200
    return jsonify(res_obj), http_code






