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

from glygen.usecases_apilib import (
        search_init, 
        glycan_to_biosynthesis_enzymes, 
        glycan_to_glycoproteins, 
        glycan_to_enzyme_gene_loci,
        biosynthesis_enzyme_to_glycans,
        protein_to_orthologs,
        protein_to_glycosequons,
        species_to_glycosyltransferases,
        species_to_glycohydrolases,
        species_to_glycoproteins,
        disease_to_glycosyltransferases,
        genelocus_list,
        genelocus_list,
        ortholog_list,
        glycosequon_list
    )

from glygen.util import get_error_obj, trim_object
import traceback


api = Namespace("usecases", description="Usecase APIs")

search_init_query_model = api.model(
    'search_init Query', { 'query': fields.String(required=True, default="", description='')})
glycan_to_biosynthesis_enzymes_query_model = api.model(
    'glycan_to_biosynthesis_enzymes Query', { 'query': fields.String(required=True, default="", description='')})
glycan_to_glycoproteins_query_model = api.model(
    'glycan_to_glycoproteins Query', { 'query': fields.String(required=True, default="", description='')})
glycan_to_enzyme_gene_loci_query_model = api.model(
    'glycan_to_enzyme_gene_loci Query', { 'query': fields.String(required=True, default="", description='')})
biosynthesis_enzyme_to_glycans_query_model = api.model(
    'biosynthesis_enzyme_to_glycans Query', { 'query': fields.String(required=True, default="", description='')})
protein_to_orthologs_query_model = api.model(
    'protein_to_orthologs Query', { 'query': fields.String(required=True, default="", description='')})
protein_to_glycosequons_query_model = api.model(
    'protein_to_glycosequons Query', { 'query': fields.String(required=True, default="", description='')})
species_to_glycosyltransferases_query_model = api.model(
    'species_to_glycosyltransferases Query', { 'query': fields.String(required=True, default="", description='')})
species_to_glycohydrolases_query_model = api.model(
    'species_to_glycohydrolases Query', { 'query': fields.String(required=True, default="", description='')})
species_to_glycoproteins_query_model = api.model(
    'species_to_glycoproteins Query', { 'query': fields.String(required=True, default="", description='')})
disease_to_glycosyltransferases_query_model = api.model(
    'disease_to_glycosyltransferases Query', { 'query': fields.String(required=True, default="", description='')})
genelocus_list_query_model = api.model(
    'genelocus_list Query', { 'query': fields.String(required=True, default="", description='')})
genelocus_list_query_model = api.model(
    'genelocus_list Query', { 'query': fields.String(required=True, default="", description='')})
ortholog_list_query_model = api.model(
    'ortholog_list Query', { 'query': fields.String(required=True, default="", description='')})
glycosequon_list_query_model = api.model(
    'glycosequon_list Query', { 'query': fields.String(required=True, default="", description='')})

@api.route('/search_init/')
class Usecases(Resource):
    @api.doc('search_init')
    @api.expect(search_init_query_model)
    def post(self):
        api_name = "search_init"
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        res_obj = {}
        try:
            req_obj = request.json
            trim_object(req_obj)
            data_path = os.environ["DATA_PATH"]
            res_obj = search_init(config_obj)
        except Exception as e:
            log_path = current_app.config["LOG_PATH"] 
            res_obj = get_error_obj(api_name, traceback.format_exc(), log_path)
        return res_obj

    def get(self):
        return self.post()


@api.route('/glycan_to_biosynthesis_enzymes/<tax_id>/<glytoucan_ac>/')
class Usecases(Resource):
    @api.doc('glycan_to_biosynthesis_enzymes')
    def post(self, tax_id, glytoucan_ac):
        api_name = "glycan_to_biosynthesis_enzymes"
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        res_obj = {}
        try:
            req_obj = {"glytoucan_ac":glytoucan_ac, "tax_id":int(tax_id)}
            data_path = os.environ["DATA_PATH"]
            res_obj = glycan_to_biosynthesis_enzymes(req_obj, config_obj)
        except Exception as e:
            log_path = current_app.config["LOG_PATH"]
            res_obj = get_error_obj(api_name, traceback.format_exc(), log_path)
        return res_obj

    def get(self, tax_id, glytoucan_ac):
        return self.post(tax_id, glytoucan_ac)


@api.route('/glycan_to_glycoproteins/<tax_id>/<glytoucan_ac>/')
class Usecases(Resource):
    @api.doc('glycan_to_glycoproteins')
    def post(self, tax_id, glytoucan_ac):
        api_name = "glycan_to_glycoproteins"
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        res_obj = {}
        try:
            req_obj = {"glytoucan_ac":glytoucan_ac, "tax_id":int(tax_id)}
            data_path = os.environ["DATA_PATH"]
            res_obj = glycan_to_glycoproteins(req_obj, config_obj)
        except Exception as e:
            log_path = current_app.config["LOG_PATH"]
            res_obj = get_error_obj(api_name, traceback.format_exc(), log_path)
        return res_obj
    
    def get(self, tax_id, glytoucan_ac):
        return self.post(tax_id, glytoucan_ac)



@api.route('/glycan_to_enzyme_gene_loci/<tax_id>/<glytoucan_ac>/')
class Usecases(Resource):
    @api.doc('glycan_to_enzyme_gene_loci')
    def post(self, tax_id, glytoucan_ac):
        api_name = "glycan_to_enzyme_gene_loci"
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        res_obj = {}
        try:
            req_obj = {"glytoucan_ac":glytoucan_ac, "tax_id":int(tax_id)}
            data_path = os.environ["DATA_PATH"]
            res_obj = glycan_to_enzyme_gene_loci(req_obj, config_obj)
        except Exception as e:
            log_path = current_app.config["LOG_PATH"]
            res_obj = get_error_obj(api_name, traceback.format_exc(), log_path)
        return res_obj

    def get(self, tax_id, glytoucan_ac):
        return self.post(tax_id, glytoucan_ac)


@api.route('/biosynthesis_enzyme_to_glycans/')
class Usecases(Resource):
    @api.doc('biosynthesis_enzyme_to_glycans')
    @api.expect(biosynthesis_enzyme_to_glycans_query_model)
    def post(self):
        api_name = "biosynthesis_enzyme_to_glycans"
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        res_obj = {}
        try:
            req_obj = request.json
            trim_object(req_obj)
            data_path = os.environ["DATA_PATH"]
            res_obj = biosynthesis_enzyme_to_glycans(req_obj, config_obj)
        except Exception as e:
            log_path = current_app.config["LOG_PATH"]
            res_obj = get_error_obj(api_name, traceback.format_exc(), log_path)
        return res_obj

    def get(self):
        return self.post()


@api.route('/protein_to_orthologs/<uniprot_canonical_ac>/')
class Usecases(Resource):
    @api.doc('protein_to_orthologs')
    def post(self, uniprot_canonical_ac):
        api_name = "protein_to_orthologs"
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        res_obj = {}
        try:
            req_obj = {"uniprot_canonical_ac":uniprot_canonical_ac}
            data_path = os.environ["DATA_PATH"]
            res_obj = protein_to_orthologs(req_obj, config_obj)
        except Exception as e:
            log_path = current_app.config["LOG_PATH"]
            res_obj = get_error_obj(api_name, traceback.format_exc(), log_path)
        return res_obj

    def get(self, uniprot_canonical_ac):
        return self.post(uniprot_canonical_ac)



@api.route('/protein_to_glycosequons/<uniprot_canonical_ac>/')
class Usecases(Resource):
    @api.doc('protein_to_glycosequons')
    def post(self, uniprot_canonical_ac):
        api_name = "protein_to_glycosequons"
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        res_obj = {}
        try:
            req_obj = {"uniprot_canonical_ac":uniprot_canonical_ac}
            data_path = os.environ["DATA_PATH"]
            res_obj = protein_to_glycosequons(req_obj, config_obj)
        except Exception as e:
            log_path = current_app.config["LOG_PATH"]
            res_obj = get_error_obj(api_name, traceback.format_exc(), log_path)
        return res_obj

    def get(self, uniprot_canonical_ac):
        return self.post(uniprot_canonical_ac)



@api.route('/species_to_glycosyltransferases/<tax_id>/')
class Usecases(Resource):
    @api.doc('species_to_glycosyltransferases')
    def post(self, tax_id):
        api_name = "species_to_glycosyltransferases"
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        res_obj = {}
        try:
            req_obj = {"tax_id":int(tax_id)}
            data_path = os.environ["DATA_PATH"]
            res_obj = species_to_glycosyltransferases(req_obj, config_obj)
        except Exception as e:
            log_path = current_app.config["LOG_PATH"]
            res_obj = get_error_obj(api_name, traceback.format_exc(), log_path)
        return res_obj

    def get(self, tax_id):
        return self.post(tax_id)

@api.route('/species_to_glycohydrolases/<tax_id>/')
class Usecases(Resource):
    @api.doc('species_to_glycohydrolases')
    def post(self, tax_id):
        api_name = "species_to_glycohydrolases"
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        res_obj = {}
        try:
            req_obj = {"tax_id":int(tax_id)} 
            data_path = os.environ["DATA_PATH"]
            res_obj = species_to_glycohydrolases(req_obj, config_obj)
        except Exception as e:
            log_path = current_app.config["LOG_PATH"]
            res_obj = get_error_obj(api_name, traceback.format_exc(), log_path)
        return res_obj
    
    def get(self, tax_id):
        return self.post(tax_id)

@api.route('/species_to_glycoproteins/<tax_id>/<evidence_type>/')
class Usecases(Resource):
    @api.doc('species_to_glycoproteins')
    def post(self, tax_id, evidence_type):
        api_name = "species_to_glycoproteins"
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        res_obj = {}
        try:
            req_obj = {"tax_id":int(tax_id), "evidence_type":evidence_type} 
            data_path = os.environ["DATA_PATH"]
            res_obj = species_to_glycoproteins(req_obj, config_obj)
        except Exception as e:
            log_path = current_app.config["LOG_PATH"]
            res_obj = get_error_obj(api_name, traceback.format_exc(), log_path)
        return res_obj

    def get(self, tax_id, evidence_type):
        return self.post(tax_id, evidence_type)

@api.route('/disease_to_glycosyltransferases/')
class Usecases(Resource):
    @api.doc('disease_to_glycosyltransferases')
    @api.expect(disease_to_glycosyltransferases_query_model)
    def post(self):
        api_name = "disease_to_glycosyltransferases"
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        res_obj = {}
        try:
            req_obj = request.json
            trim_object(req_obj)
            data_path = os.environ["DATA_PATH"]
            res_obj = disease_to_glycosyltransferases(req_obj, config_obj)
        except Exception as e:
            log_path = current_app.config["LOG_PATH"]
            res_obj = get_error_obj(api_name, traceback.format_exc(), log_path)
        return res_obj

    def get(self):
        return self.post()


@api.route('/genelocus_list/')
class Usecases(Resource):
    @api.doc('genelocus_list')
    @api.expect(genelocus_list_query_model)
    def post(self):
        api_name = "genelocus_list"
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        res_obj = {}
        try:
            req_obj = request.json
            trim_object(req_obj)
            data_path = os.environ["DATA_PATH"]
            res_obj = genelocus_list(req_obj, config_obj)
        except Exception as e:
            log_path = current_app.config["LOG_PATH"]
            res_obj = get_error_obj(api_name, traceback.format_exc(), log_path)
        return res_obj

    def get(self):
        return self.post()



@api.route('/genelocus_list/')
class Usecases(Resource):
    @api.doc('genelocus_list')
    @api.expect(genelocus_list_query_model)
    def post(self):
        api_name = "genelocus_list"
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        res_obj = {}
        try:
            req_obj = request.json
            trim_object(req_obj)
            data_path = os.environ["DATA_PATH"]
            res_obj = genelocus_list(req_obj, config_obj)
        except Exception as e:
            log_path = current_app.config["LOG_PATH"]
            res_obj = get_error_obj(api_name, traceback.format_exc(), log_path)
        return res_obj

    def get(self):
        return self.post()



@api.route('/ortholog_list/')
class Usecases(Resource):
    @api.doc('ortholog_list')
    @api.expect(ortholog_list_query_model)
    def post(self):
        api_name = "ortholog_list"
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        res_obj = {}
        try:
            req_obj = request.json
            trim_object(req_obj)
            data_path = os.environ["DATA_PATH"]
            res_obj = ortholog_list(req_obj, config_obj)
        except Exception as e:
            log_path = current_app.config["LOG_PATH"]
            res_obj = get_error_obj(api_name, traceback.format_exc(), log_path)
        return res_obj

    def get(self):
        return self.post()



@api.route('/glycosequon_list/')
class Usecases(Resource):
    @api.doc('glycosequon_list')
    @api.expect(glycosequon_list_query_model)
    def post(self):
        api_name = "glycosequon_list"
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        res_obj = {}
        try:
            req_obj = request.json
            trim_object(req_obj)
            data_path = os.environ["DATA_PATH"]
            res_obj = glycosequon_list(req_obj, config_obj)
        except Exception as e:
            log_path = current_app.config["LOG_PATH"]
            res_obj = get_error_obj(api_name, traceback.format_exc(), log_path)
        return res_obj
    
    def get(self):
        return self.post()





