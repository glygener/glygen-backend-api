import os,sys
import json
import traceback
import csv
import requests
from flask import (Blueprint,request,jsonify,current_app)
from gsa.db import get_mongodb, log_error, next_sequence_value
from flask_restx import Resource, Api
from flask_mail import Mail, Message

from werkzeug.utils import secure_filename

bp = Blueprint('misc', __name__, url_prefix='/misc')

#api = Api(current_app)
api = Api(bp)


@bp.route('/hello', methods=('GET', 'POST'))
class HelloWorld(Resource):
    def hello(self):
        return "Hello!"



@bp.route('/hello_world', methods=('GET', 'POST'))
def hello_world():
    res_obj = {
        "message":"Hello World!",
        "instance_path":current_app.instance_path,
        "secret_key":current_app.config["SECRET_KEY"]
    }
    return jsonify(res_obj), 200


@bp.route('/upload', methods=('GET', 'POST'))
def upload():
    
    res_obj = {"config":{}}
    error_list = []
    if request.method != 'POST':
        error_list.append({"error":"only POST requests are accepted"})
    elif 'file' not in request.files:
        error_list.append({"error":"no file parameter given"})
    else:
        file = request.files['file']
        if file.filename == '':
            error_list.append({"error":"no filename given"})
        else:
            file_name = secure_filename(file.filename)
            out_file = os.path.join(current_app.config['DATA_PATH'], file_name)
            res_obj["out_file"] = out_file
            file.save(out_file)

    if error_list != []:
        return jsonify({"error_list":error_list}), 200

    return jsonify(res_obj), 200



@bp.route('/info', methods=('GET', 'POST'))
def info():
    res_obj = {"config":{}}
    #k_list = ["DB_HOST", "DB_NAME", "DB_USERNAME", "DB_PASSWORD",  "DATA_PATH"]
    #k_list = ["DB_HOST", "DB_NAME", "DB_USERNAME",  "DATA_PATH", "MAX_CONTENT_LENGTH"]
    k_list = ["SERVER","MAIL_SERVER", "MAIL_PORT", "MAIL_USE_TLS", "MAIL_USE_SSL", 
            "MAIL_USERNAME", "MAIL_PASSWORD"]    
    #k_list = ["DATA_PATH", "MAX_CONTENT_LENGTH"]
    for k in k_list:
        res_obj["config"][k] = current_app.config[k]
    mongo_dbh, error_obj = get_mongodb()
    res_obj["connection_status"] = "success" if error_obj == {} else error_obj
    return jsonify(res_obj), 200


@bp.route('/urlexists', methods=('GET', 'POST'))
def urlexists():

    req_obj = request.json
    res_obj = {}
    try:
        response = requests.get(req_obj["url"])
        if response.status_code in [200, 403]:
            res_obj = {"status":1}
        else:
            res_obj = {"status":0, "code":response.status_code}
    except Exception as e:
        res_obj = {"status":0, "error":"unable to check url!"}

    return jsonify(res_obj), 200


@bp.route('/taxidexists', methods=('GET', 'POST'))
def taxidexists():

    req_obj = request.json
    res_obj = {"status":0}
    try:
        url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=taxonomy&retmode=json&id="
        url += req_obj["tax_id"]
        response = requests.get(url)
        if response.status_code == 200:
            res = response.json()
            if "error" not in res:
                tax_id = str(req_obj["tax_id"])
                org_name = res["result"][tax_id]["scientificname"]
                res_obj = {"status":1, "orgname":org_name}
    except Exception as e:
        res_obj = {"status":0, "error":"unable to check url!"}

    return jsonify(res_obj), 200


@bp.route('/sendmail', methods=('GET', 'POST'))
def sendmail():


    #current_app.config["MAIL_SERVER"] = "localhost"
    
    res_obj = {}
    try:
        msg = Message(
            "Authentication code from GSA", 
            sender = current_app.config["MAIL_SENDER"], 
            recipients = ["rykahsay@gwu.edu"]
        )
        msg.body = "Your code is 112233"
        mail = Mail(current_app)
        mail.send(msg)
        res_obj = {"status":"success"}
    except Exception as e:
        res_obj =  log_error(traceback.format_exc())

    return jsonify(res_obj), 200
