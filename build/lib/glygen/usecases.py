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

from glygen.util import get_req_obj
import traceback


api = Namespace("usecases", description="Usecase APIs")

search_init_query_model = api.model("Usecases Search Init Query", {})


disease_to_glycosyltransferases_query_model = api.model("disease_to_glycosyltransferases Query", 
    { 
        "tax_id": fields.Integer(required=True, default=9606),
        "do_name": fields.String(required=True, default="Gilbert syndrom")
    }
)

genelocus_list_query_model = api.model("Gene Locus List Query",
    { "id": fields.String(required=True, default="")}
)
ortholog_list_query_model = api.model("Ortholog List Query",
    { 
        "id": fields.String(required=True, default=""),
        "sort": fields.String(required=True, default="uniprot_canonical_ac")
    }
)
glycosequon_list_query_model = api.model("Glycosequon List Query",
    {
        "id": fields.String(required=True, default=""),
        "sort": fields.String(required=True, default="start_pos")
    }
)


@api.route('/search_init/')
class Usecases(Resource):
    @api.expect(search_init_query_model)
    def post(self):
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        res_obj = {}
        try:
            data_path = os.environ["DATA_PATH"]
            res_obj = log_request({}, "/usecases/search_init/", request)
            if "error_list" not in res_obj:
                res_obj = search_init(config_obj)
        except Exception as e:
            res_obj = log_error(traceback.format_exc())
        http_code = 500 if "error_list" in res_obj else 200
        return res_obj, http_code

    @api.doc(False)
    def get(self):
        return self.post()


@api.route('/glycan_to_biosynthesis_enzymes/<tax_id>/<glytoucan_ac>/')
@api.doc(params={
    "tax_id": {"in": "query", "default": 9606}, "glytoucan_ac": {"in": "query", "default": "G17689DH"}
})
class Usecases(Resource):
    def post(self, tax_id, glytoucan_ac):
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        res_obj = {}
        try:
            req_obj = {"glytoucan_ac":glytoucan_ac, "tax_id":int(tax_id)}
            data_path = os.environ["DATA_PATH"]
            res_obj = log_request(req_obj, "/usecases/glycan_to_biosynthesis_enzymes/", request)
            if "error_list" not in res_obj:
                res_obj = glycan_to_biosynthesis_enzymes(req_obj, config_obj)
        except Exception as e:
            res_obj = log_error(traceback.format_exc())
        http_code = 500 if "error_list" in res_obj else 200
        return res_obj, http_code

    @api.doc(False)
    def get(self, tax_id, glytoucan_ac):
        return self.post(tax_id, glytoucan_ac)


@api.route('/glycan_to_glycoproteins/<tax_id>/<glytoucan_ac>/')
@api.doc(params={
    "tax_id": {"in": "query", "default": 9606}, "glytoucan_ac": {"in": "query", "default": "G17689DH"}
})
class Usecases(Resource):
    def post(self, tax_id, glytoucan_ac):
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        res_obj = {}
        try:
            req_obj = {"glytoucan_ac":glytoucan_ac, "tax_id":int(tax_id)}
            data_path = os.environ["DATA_PATH"]
            res_obj = log_request(req_obj, "/usecases/glycan_to_glycoproteins/", request)
            if "error_list" not in res_obj:
                res_obj = glycan_to_glycoproteins(req_obj, config_obj)
        except Exception as e:
            res_obj = log_error(traceback.format_exc())
        http_code = 500 if "error_list" in res_obj else 200
        return res_obj, http_code
    
    @api.doc(False)
    def get(self, tax_id, glytoucan_ac):
        return self.post(tax_id, glytoucan_ac)



@api.route('/glycan_to_enzyme_gene_loci/<tax_id>/<glytoucan_ac>/')
@api.doc(params={
    "tax_id": {"in": "query", "default": 9606}, "glytoucan_ac": {"in": "query", "default": "G17689DH"}
})
class Usecases(Resource):
    def post(self, tax_id, glytoucan_ac):
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        res_obj = {}
        try:
            req_obj = {"glytoucan_ac":glytoucan_ac, "tax_id":int(tax_id)}
            data_path = os.environ["DATA_PATH"]
            res_obj = log_request(req_obj, "/usecases/glycan_to_enzyme_gene_loci/", request)
            if "error_list" not in res_obj:
                res_obj = glycan_to_enzyme_gene_loci(req_obj, config_obj)
        except Exception as e:
            res_obj = log_error(traceback.format_exc())
        http_code = 500 if "error_list" in res_obj else 200
        return res_obj, http_code

    @api.doc(False)
    def get(self, tax_id, glytoucan_ac):
        return self.post(tax_id, glytoucan_ac)


@api.route('/biosynthesis_enzyme_to_glycans/<tax_id>/<uniprot_canonical_ac>/')
@api.doc(params={
    "tax_id": {"in": "query", "default": 9606},
    "uniprot_canonical_ac": {"in": "query", "default": "P26572-1"}
    }
)
class Usecases(Resource):
    def post(self, tax_id, uniprot_canonical_ac):
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        res_obj = {}
        try:
            req_obj = {"uniprot_canonical_ac":uniprot_canonical_ac, "tax_id":int(tax_id)}
            data_path = os.environ["DATA_PATH"]
            res_obj = log_request(req_obj, "/usecases/biosynthesis_enzyme_to_glycans/", request)
            if "error_list" not in res_obj:
                res_obj = biosynthesis_enzyme_to_glycans(req_obj, config_obj)
        except Exception as e:
            res_obj = log_error(traceback.format_exc())
        http_code = 500 if "error_list" in res_obj else 200
        return res_obj, http_code

    @api.doc(False)
    def get(self, tax_id, uniprot_canonical_ac):
        return self.post(tax_id, uniprot_canonical_ac)


@api.route('/protein_to_orthologs/<uniprot_canonical_ac>/')
@api.doc(params={"uniprot_canonical_ac": {"in": "query", "default": "P14210-1"}})
class Usecases(Resource):
    def post(self, uniprot_canonical_ac):
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        res_obj = {}
        try:
            req_obj = {"uniprot_canonical_ac":uniprot_canonical_ac}
            data_path = os.environ["DATA_PATH"]
            res_obj = log_request(req_obj, "/usecases/protein_to_orthologs/", request)
            if "error_list" not in res_obj:
                res_obj = protein_to_orthologs(req_obj, config_obj)
        except Exception as e:
            res_obj = log_error(traceback.format_exc())
        
        http_code = 500 if "error_list" in res_obj else 200
        return res_obj, http_code

    @api.doc(False)
    def get(self, uniprot_canonical_ac):
        return self.post(uniprot_canonical_ac)



@api.route('/protein_to_glycosequons/<uniprot_canonical_ac>/')
@api.doc(params={"uniprot_canonical_ac": {"in": "query", "default": "P14210-1"}})
class Usecases(Resource):
    def post(self, uniprot_canonical_ac):
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        res_obj = {}
        try:
            req_obj = {"uniprot_canonical_ac":uniprot_canonical_ac}
            data_path = os.environ["DATA_PATH"]
            res_obj = log_request(req_obj, "/usecases/protein_to_glycosequons/", request)
            if "error_list" not in res_obj:
                res_obj = protein_to_glycosequons(req_obj, config_obj)
        except Exception as e:
            res_obj = log_error(traceback.format_exc())
        http_code = 500 if "error_list" in res_obj else 200
        return res_obj, http_code

    @api.doc(False)
    def get(self, uniprot_canonical_ac):
        return self.post(uniprot_canonical_ac)



@api.route('/species_to_glycosyltransferases/<tax_id>/')
@api.doc(params={"tax_id": {"in": "query", "default": 9606}})
class Usecases(Resource):
    def post(self, tax_id):
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        res_obj = {}
        try:
            req_obj = {"tax_id":int(tax_id)}
            data_path = os.environ["DATA_PATH"]
            res_obj = log_request(req_obj, "/usecases/species_to_glycosyltransferases/", request)
            if "error_list" not in res_obj:
                res_obj = species_to_glycosyltransferases(req_obj, config_obj)
        except Exception as e:
            res_obj = log_error(traceback.format_exc())
        http_code = 500 if "error_list" in res_obj else 200
        return res_obj, http_code

    @api.doc(False)
    def get(self, tax_id):
        return self.post(tax_id)

@api.route('/species_to_glycohydrolases/<tax_id>/')
@api.doc(params={"tax_id": {"in": "query", "default": 9606}})
class Usecases(Resource):
    def post(self, tax_id):
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        res_obj = {}
        try:
            req_obj = {"tax_id":int(tax_id)} 
            data_path = os.environ["DATA_PATH"]
            res_obj = log_request(req_obj, "/usecases/species_to_glycohydrolases/", request)
            if "error_list" not in res_obj:
                res_obj = species_to_glycohydrolases(req_obj, config_obj)
        except Exception as e:
            res_obj = log_error(traceback.format_exc())
        http_code = 500 if "error_list" in res_obj else 200
        return res_obj, http_code
    
    @api.doc(False)
    def get(self, tax_id):
        return self.post(tax_id)

@api.route('/species_to_glycoproteins/<tax_id>/<evidence_type>/')
@api.doc(params={"tax_id": {"in": "query", "default": 9606}, "evidence_type":{"in": "query", "default": "reported"}})
class Usecases(Resource):
    def post(self, tax_id, evidence_type):
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        res_obj = {}
        try:
            req_obj = {"tax_id":int(tax_id), "evidence_type":evidence_type} 
            data_path = os.environ["DATA_PATH"]
            res_obj = log_request(req_obj, "/usecases/species_to_glycoproteins/", request)
            if "error_list" not in res_obj:
                res_obj = species_to_glycoproteins(req_obj, config_obj)
        except Exception as e:
            res_obj = log_error(traceback.format_exc())
        http_code = 500 if "error_list" in res_obj else 200
        return res_obj, http_code

    @api.doc(False)
    def get(self, tax_id, evidence_type):
        return self.post(tax_id, evidence_type)

@api.route('/disease_to_glycosyltransferases/')
class Usecases(Resource):
    @api.expect(disease_to_glycosyltransferases_query_model)
    def post(self):
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        res_obj = {}
        try:
            req_obj = get_req_obj(request)
            data_path = os.environ["DATA_PATH"]
            res_obj = log_request(req_obj, "/usecases/disease_to_glycosyltransferases/", request)
            if "error_list" not in res_obj:
                res_obj = disease_to_glycosyltransferases(req_obj, config_obj)
        except Exception as e:
            res_obj = log_error(traceback.format_exc())
        http_code = 500 if "error_list" in res_obj else 200
        return res_obj, http_code

    @api.doc(False)
    def get(self):
        return self.post()


@api.route('/genelocus_list/')
class Usecases(Resource):
    @api.expect(genelocus_list_query_model)
    def post(self):
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        res_obj = {}
        try:
            req_obj = get_req_obj(request)
            data_path = os.environ["DATA_PATH"]
            res_obj = log_request(req_obj, "/usecases/genelocus_list/", request)
            if "error_list" not in res_obj:
                res_obj = genelocus_list(req_obj, config_obj)
        except Exception as e:
            res_obj = log_error(traceback.format_exc())
        http_code = 500 if "error_list" in res_obj else 200
        return res_obj, http_code

    @api.doc(False)
    def get(self):
        return self.post()



@api.route('/genelocus_list/')
class Usecases(Resource):
    @api.expect(genelocus_list_query_model)
    def post(self):
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        res_obj = {}
        try:
            req_obj = get_req_obj(request)
            data_path = os.environ["DATA_PATH"]
            res_obj = log_request(req_obj, "/usecases/genelocus_list/", request)
            if "error_list" not in res_obj:
                res_obj = genelocus_list(req_obj, config_obj)
        except Exception as e:
            res_obj = log_error(traceback.format_exc())
        http_code = 500 if "error_list" in res_obj else 200
        return res_obj, http_code

    @api.doc(False)
    def get(self):
        return self.post()



@api.route('/ortholog_list/')
class Usecases(Resource):
    @api.expect(ortholog_list_query_model)
    def post(self):
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        res_obj = {}
        try:
            req_obj = get_req_obj(request)
            data_path = os.environ["DATA_PATH"]
            res_obj = log_request(req_obj, "/usecases/ortholog_list/", request)
            if "error_list" not in res_obj:
                res_obj = ortholog_list(req_obj, config_obj)
        except Exception as e:
            res_obj = log_error(traceback.format_exc())
        http_code = 500 if "error_list" in res_obj else 200
        return res_obj, http_code

    @api.doc(False)
    def get(self):
        return self.post()



@api.route('/glycosequon_list/')
class Usecases(Resource):
    @api.expect(glycosequon_list_query_model)
    def post(self):
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        res_obj = {}
        try:
            req_obj = get_req_obj(request)
            data_path = os.environ["DATA_PATH"]
            res_obj = log_request(req_obj, "/usecases/glycosequon_list/", request)
            if "error_list" not in res_obj:
                res_obj = glycosequon_list(req_obj, config_obj)
        except Exception as e:
            res_obj = log_error(traceback.format_exc())
        http_code = 500 if "error_list" in res_obj else 200
        return res_obj, http_code
    
    @api.doc(False)
    def get(self):
        return self.post()





