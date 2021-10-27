import sys
import os
import json
import string
import csv
import traceback
import glycan_apilib as apilib
import errorlib
import util
import requests

from flask import Flask, request, jsonify, render_template, send_file
from flask_cors import CORS
app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False
CORS(app)


global config_obj
global path_obj

config_obj = json.loads(open("./conf/config.json", "r").read())
path_obj  =  config_obj[config_obj["server"]]["pathinfo"]


@app.route('/swagger/glycan_search/', methods=['GET', 'POST'])
def glycan_search():
 
    res_obj = {}
    try:
        query_obj = get_query_json()
        util.trim_object(query_obj)
        res_obj = apilib.glycan_search(query_obj, config_obj)
        #res_obj = query_obj
    except Exception, e:
        res_obj = errorlib.get_error_obj("swagger_glycan_search", traceback.format_exc(), path_obj)
    
    
    http_code = 500 if "error_list" in res_obj else 200
    return jsonify(res_obj), http_code



def get_query_json():

    int_list = ["number_monosaccharides.max", "number_monosaccharides.min"]
    float_list = ["mass.min", "mass.max"]
    list_list = ["organism.organism_list.id"]


    query_obj = {}
    param_dict = request.args.to_dict()
    for param in param_dict:
        if param[0:9] == "organism.":
            query_obj["organism"] = {
                "organism_list":[
                    {"id":int(param_dict["organism.organism_list.id"]), "name":param_dict["organism.organism_list.name"]}
                ],
                "operation":param_dict["organism.operation"]
            }
        else:
            val = param_dict[param].strip()
            if val == "":
                continue

            if param in float_list:
                val = float(val)
            elif param in int_list:
                val = int(val)
            elif param in list_list:
                val = [int(val)]
            key_parts = param.split(".")
            if len(key_parts) == 1:
                query_obj[key_parts[0]] = param_dict[param]
            elif len(key_parts) == 2:
                if key_parts[0] not in query_obj:
                    query_obj[key_parts[0]] = {key_parts[1]:val}
                else:
                    query_obj[key_parts[0]][key_parts[1]] = val
            elif len(key_parts) == 3:
                if key_parts[0] not in query_obj:
                    query_obj[key_parts[0]] = {key_parts[1]:{key_parts[2]:val}}
                elif key_parts[1] not in query_obj[key_parts[0]]:
                    query_obj[key_parts[0]][key_parts[1]] = {key_parts[2]:val}
                else:
                    query_obj[key_parts[0]][key_parts[1]][key_parts[2]] = val

    return query_obj
