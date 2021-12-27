import os
import json
import string
import csv
import traceback
import video_apilib as apilib
import errorlib
import util

from flask import Flask, request, jsonify, render_template, send_file
from flask_cors import CORS
app = Flask(__name__)
CORS(app)


global config_obj
global path_obj

config_obj = json.loads(open("./conf/config.json", "r").read())
path_obj  =  config_obj[config_obj["server"]]["pathinfo"]
db_info = json.loads(open("./conf/dbinfo.json", "r").read())
config_obj[config_obj["server"]]["dbinfo"] = db_info[config_obj["server"]]



@app.route('/video/addnew/', methods=['GET', 'POST'])
def video_addnew():
   
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
            res_obj = apilib.video_addnew(query_obj, config_obj)
    except Exception, e:
        res_obj = errorlib.get_error_obj("video_addnew", traceback.format_exc(), path_obj)

    http_code = 500 if "error_list" in res_obj else 200
    return jsonify(res_obj), http_code



@app.route('/video/list/', methods=['GET', 'POST'])
def video_list():

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
            res_obj = apilib.video_list(query_obj, config_obj)
    except Exception, e:
        res_obj = errorlib.get_error_obj("video_list", traceback.format_exc(), path_obj)

    http_code = 500 if "error_list" in res_obj else 200
    return jsonify(res_obj), http_code



@app.route('/video/detail/', methods=['GET', 'POST'])
def video_detail():

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
            res_obj = apilib.video_detail(query_obj, config_obj)
    except Exception, e:
        res_obj = errorlib.get_error_obj("video_detail", traceback.format_exc(), path_obj)

    http_code = 500 if "error_list" in res_obj else 200
    return jsonify(res_obj), http_code










@app.route('/video/delete/', methods=['GET', 'POST'])
def video_delete():

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
            res_obj = apilib.video_delete(query_obj, config_obj)
    except Exception, e:
        res_obj = errorlib.get_error_obj("video_delete", traceback.format_exc(), path_obj)

    http_code = 500 if "error_list" in res_obj else 200
    return jsonify(res_obj), http_code
