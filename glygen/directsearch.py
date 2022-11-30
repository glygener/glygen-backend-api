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


from glygen.directsearch_apilib import (
    protein, gene, glycan, glycan_to_biosynthesis_enzymes
    ,glycan_to_glycoproteins, biosynthesis_enzyme_to_glycans, protein_to_homologs
    ,species_to_glycosyltransferases, species_to_glycohydrolases, species_to_glycoproteins
    ,disease_to_glycosyltransferases
    )



from glygen.util import get_error_obj, trim_object
import traceback


api = Namespace("directsearch", description="Direct Search APIs")

protein_query_model = api.model(
    'Protein Query', 
    { 'query': fields.String(required=True, default="", description='')}
)

gene_query_model = api.model(
    'Gene Query',
    { 'query': fields.String(required=True, default="", description='')}
)
glycan_query_model = api.model(
    'Glycan Query',
    { 'query': fields.String(required=True, default="", description='')}
)
glycan_to_biosynthesis_enzymes_query_model = api.model(
    'Glycan to Biosynthesis Enzymes Query',
    { 'query': fields.String(required=True, default="", description='')}
)
glycan_to_glycoproteins_query_model = api.model(
    'Glycan to Glycoproteins Query',
    { 'query': fields.String(required=True, default="", description='')}
)
biosynthesis_enzyme_to_glycans_query_model = api.model(
    'Biosynthesis Enzyme to Glycans Query',
    { 'query': fields.String(required=True, default="", description='')}
)
protein_to_homologs_query_model = api.model(
    'Protein to homologs Query',
    { 'query': fields.String(required=True, default="", description='')}
)
species_to_glycosyltransferases_query_model = api.model(
    'Species to Glycosyltransferases Query',
    { 'query': fields.String(required=True, default="", description='')}
)
species_to_glycohydrolases_query_model = api.model(
    'Species to Glycohydrolases Query',
    { 'query': fields.String(required=True, default="", description='')}
)
species_to_glycoproteins_query_model = api.model(
    'Species to Glycoproteins Query',
    { 'query': fields.String(required=True, default="", description='')}
)
disease_to_glycosyltransferases_query_model = api.model(
    'Disease to Glycosyltransferases Query',
    { 'query': fields.String(required=True, default="", description='')}
)




@api.route('/protein/')
class Data(Resource):
    @api.doc('protein')
    @api.expect(protein_query_model)
    def post(self):
        api_name = "directsearch_protein"
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        res_obj = {}
        try:
            req_obj = request.json
            trim_object(req_obj)
            res_obj = protein(req_obj, config_obj)
        except Exception as e:
            log_path = current_app.config["LOG_PATH"] 
            res_obj = get_error_obj(api_name, traceback.format_exc(), log_path)
        return res_obj


@api.route('/gene/')
class Data(Resource):
    @api.doc('gene')
    @api.expect(gene_query_model)
    def post(self):
        api_name = "directsearch_gene"
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        res_obj = {}
        try:
            req_obj = request.json
            trim_object(req_obj)
            res_obj = gene(req_obj, config_obj)
        except Exception as e:
            log_path = current_app.config["LOG_PATH"]
            res_obj = get_error_obj(api_name, traceback.format_exc(), log_path)
        return res_obj



@api.route('/glycan/')
class Data(Resource):
    @api.doc('glycan')
    @api.expect(glycan_query_model)
    def post(self):
        api_name = "directsearch_glycan"
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        res_obj = {}
        try:
            req_obj = request.json
            trim_object(req_obj)
            res_obj = glycan(req_obj, config_obj)
        except Exception as e:
            log_path = current_app.config["LOG_PATH"]
            res_obj = get_error_obj(api_name, traceback.format_exc(), log_path)
        return res_obj


@api.route('/glycan_to_biosynthesis_enzymes/')
class Data(Resource):
    @api.doc('glycan_to_biosynthesis_enzymes')
    @api.expect(glycan_to_biosynthesis_enzymes_query_model)
    def post(self):
        api_name = "directsearch_glycan_to_biosynthesis_enzymes"
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        res_obj = {}
        try:
            req_obj = request.json
            trim_object(req_obj)
            res_obj = glycan_to_biosynthesis_enzymes(req_obj, config_obj)
        except Exception as e:
            log_path = current_app.config["LOG_PATH"]
            res_obj = get_error_obj(api_name, traceback.format_exc(), log_path)
        return res_obj


@api.route('/glycan_to_glycoproteins/')
class Data(Resource):
    @api.doc('glycan_to_glycoproteins')
    @api.expect(glycan_to_glycoproteins_query_model)
    def post(self):
        api_name = "directsearch_glycan_to_glycoproteins"
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        res_obj = {}
        try:
            req_obj = request.json
            trim_object(req_obj)
            res_obj = glycan_to_glycoproteins(req_obj, config_obj)
        except Exception as e:
            log_path = current_app.config["LOG_PATH"]
            res_obj = get_error_obj(api_name, traceback.format_exc(), log_path)
        return res_obj



@api.route('/biosynthesis_enzyme_to_glycans/')
class Data(Resource):
    @api.doc('biosynthesis_enzyme_to_glycans')
    @api.expect(biosynthesis_enzyme_to_glycans_query_model)
    def post(self):
        api_name = "directsearch_biosynthesis_enzyme_to_glycans"
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        res_obj = {}
        try:
            req_obj = request.json
            trim_object(req_obj)
            res_obj = biosynthesis_enzyme_to_glycans(req_obj, config_obj)
        except Exception as e:
            log_path = current_app.config["LOG_PATH"]
            res_obj = get_error_obj(api_name, traceback.format_exc(), log_path)
        return res_obj



@api.route('/protein_to_homologs/')
class Data(Resource):
    @api.doc('protein_to_homologs')
    @api.expect(protein_to_homologs_query_model)
    def post(self):
        api_name = "directsearch_protein_to_homologs"
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        res_obj = {}
        try:
            req_obj = request.json
            trim_object(req_obj)
            res_obj = protein_to_homologs(req_obj, config_obj)
        except Exception as e:
            log_path = current_app.config["LOG_PATH"]
            res_obj = get_error_obj(api_name, traceback.format_exc(), log_path)
        return res_obj



@api.route('/species_to_glycosyltransferases/')
class Data(Resource):
    @api.doc('species_to_glycosyltransferases')
    @api.expect(species_to_glycosyltransferases_query_model)
    def post(self):
        api_name = "directsearch_species_to_glycosyltransferases"
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        res_obj = {}
        try:
            req_obj = request.json
            trim_object(req_obj)
            res_obj = species_to_glycosyltransferases(req_obj, config_obj)
        except Exception as e:
            log_path = current_app.config["LOG_PATH"]
            res_obj = get_error_obj(api_name, traceback.format_exc(), log_path)
        return res_obj



@api.route('/species_to_glycohydrolases/')
class Data(Resource):
    @api.doc('species_to_glycohydrolases')
    @api.expect(species_to_glycohydrolases_query_model)
    def post(self):
        api_name = "directsearch_species_to_glycohydrolases"
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        res_obj = {}
        try:
            req_obj = request.json
            trim_object(req_obj)
            res_obj = species_to_glycohydrolases(req_obj, config_obj)
        except Exception as e:
            log_path = current_app.config["LOG_PATH"]
            res_obj = get_error_obj(api_name, traceback.format_exc(), log_path)
        return res_obj



@api.route('/species_to_glycoproteins/')
class Data(Resource):
    @api.doc('species_to_glycoproteins')
    @api.expect(species_to_glycoproteins_query_model)
    def post(self):
        api_name = "directsearch_species_to_glycoproteins"
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        res_obj = {}
        try:
            req_obj = request.json
            trim_object(req_obj)
            res_obj = species_to_glycoproteins(req_obj, config_obj)
        except Exception as e:
            log_path = current_app.config["LOG_PATH"]
            res_obj = get_error_obj(api_name, traceback.format_exc(), log_path)
        return res_obj



@api.route('/disease_to_glycosyltransferases/')
class Data(Resource):
    @api.doc('disease_to_glycosyltransferases')
    @api.expect(disease_to_glycosyltransferases_query_model)
    def post(self):
        api_name = "directsearch_disease_to_glycosyltransferases"
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        res_obj = {}
        try:
            req_obj = request.json
            trim_object(req_obj)
            res_obj = disease_to_glycosyltransferases(req_obj, config_obj)
        except Exception as e:
            log_path = current_app.config["LOG_PATH"]
            res_obj = get_error_obj(api_name, traceback.format_exc(), log_path)
        return res_obj







