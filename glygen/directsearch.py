import os,sys
from flask_restx import Namespace, Resource, fields
from flask import (request, current_app, send_file)
from glygen.db import log_error
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


from glygen.directsearch_apilib import (
    protein, gene, glycan, glycan_to_biosynthesis_enzymes
    ,glycan_to_glycoproteins, biosynthesis_enzyme_to_glycans, protein_to_homologs
    ,species_to_glycosyltransferases, species_to_glycohydrolases, species_to_glycoproteins
    ,disease_to_glycosyltransferases
    )


from glygen.util import trim_object
import traceback


api = Namespace("directsearch", description="Direct Search APIs")

protein_query_model = api.model(
    "Direct Protein Search", 
    { 
        "uniprot_canonical_ac": fields.String(required=True, default="P12314")
    }
)

TAX_ID = api.model("TAX_ID", {"id": fields.Integer(required=True, default=9606)})
gene_query_model = api.model(
    "Direct Gene Search",
    { 
        "recommended_gene_name": fields.String(required=True, default="HGF"),
        "organism": fields.Nested(TAX_ID)
    }
)

glycan_query_model = api.model(
    "Direct Glycan Search",
    { 
        "protein_identifier": fields.String(required=True, default="P14210")
    }
)


@api.route('/protein/')
class Data(Resource):
    @api.expect(protein_query_model)
    def post(self):
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        res_obj = {}
        try:
            req_obj = request.json
            trim_object(req_obj)
            res_obj = protein(req_obj, config_obj)
        except Exception as e:
            res_obj = log_error(traceback.format_exc())
        return res_obj

    @api.doc(False)
    def get(self):
        return self.post()


@api.route('/gene/')
class Data(Resource):
    @api.expect(gene_query_model)
    def post(self):
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        res_obj = {}
        try:
            req_obj = request.json
            trim_object(req_obj)
            res_obj = gene(req_obj, config_obj)
        except Exception as e:
            res_obj = log_error(traceback.format_exc())
        return res_obj

    @api.doc(False)
    def get(self):
        return self.post()


@api.route('/glycan/')
class Data(Resource):
    @api.expect(glycan_query_model)
    def post(self):
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        res_obj = {}
        try:
            req_obj = request.json
            trim_object(req_obj)
            res_obj = glycan(req_obj, config_obj)
        except Exception as e:
            res_obj = log_error(traceback.format_exc())
        return res_obj

    @api.doc(False)
    def get(self):
        return self.post()







