import os,sys
import json
import traceback
from flask import (Blueprint,request,jsonify)
from gsa.db import get_mongodb, log_error, next_sequence_value

from flask_jwt_extended import (
    jwt_required, jwt_refresh_token_required, get_jwt_identity
)

from flask_cors import cross_origin



bp = Blueprint('pdataset', __name__, url_prefix='/pdataset')


@bp.route('/get_one', methods=('GET', 'POST'))
@jwt_required
def get_one():
    
    current_user = get_jwt_identity()
    res_obj = {}
    try:
        req_obj = request.json
        ret_obj, status = get_record_doc(req_obj)
        if status == 0:
            return jsonify(ret_obj), 200
        res_obj = {"record":ret_obj, "query":req_obj, "status":1}
    except Exception as e:
        res_obj =  log_error(traceback.format_exc())

    return jsonify(res_obj), 200



