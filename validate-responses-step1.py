import sys,os
import json
import string
import csv
import traceback
import time
from optparse import OptionParser

import jsonref
from jsonschema import validate, Draft4Validator

import jsonschema
import simplejson
import requests

import urllib3
urllib3.disable_warnings()

import libgly



def main():


    usage = "\n%prog  [options]"
    parser = OptionParser(usage,version="%prog version___")
    parser.add_option("-s","--server",action="store",dest="server",help="dev|tst|beta|prd")
    
    (options,args) = parser.parse_args()
    for key in ([options.server]):
        if not (key):
            parser.print_help()
            sys.exit(0)

    server = options.server
    api_base_url = "https://api.glygen.org/"
    if server in ["dev", "tst"]:
        api_base_url = "https://api.%s.glygen.org/" % (server)
    elif server in ["beta"]:
        api_base_url = "https://%s-api.glygen.org/" % (server)

    api_cgi_dir = "/var/www/cgi-bin/api/"
    if server == "beta":
        api_cgi_dir = "/var/www/cgi-bin/beta/api/"


    global config_obj
    global path_obj
    config_obj = json.loads(open(api_cgi_dir +  "conf/config.json", "r").read())
    path_obj  =  config_obj[config_obj["server"]]["pathinfo"]
    db_obj = config_obj[config_obj["server"]]["dbinfo"]

    

    try:
        res_obj = {}
        svc_obj_list = simplejson.loads(open(api_cgi_dir + "conf/validation.conf", "r").read())
        protein_list_id = ""
        glycan_list_id = ""
        o_list_one, o_list_two = [], []
        for o in svc_obj_list:
            if o["svc"] not in ["glycan_list", "protein_list"]:
                o_list_one.append(o)
            else:
                o_list_two.append(o)

        for svc_obj in o_list_one + o_list_two:
            json_obj = {}
            svc_name = svc_obj["svc"]
            if svc_name == "protein_list":
                svc_obj["query"]["id"] = protein_list_id
            elif svc_name == "glycan_list":
                svc_obj["query"]["id"] = glycan_list_id
            
            query_url = svc_obj["apiurl"] if "apiurl" in svc_obj else ""
            if svc_name in ["protein_detail", "glycan_detail", 
                    "protein_to_glycosequons","protein_to_orthologs",
                    "species_to_glycosyltransferases",
                    "species_to_glycohydrolases",
                    "protein_to_orthologs"
                ]:
                example_id = svc_obj["query"].values()[0]
                query_url = "%s%s/" % (svc_obj["apiurl"], example_id)
            elif svc_name in ["species_to_glycoproteins"]:
                example_id = svc_obj["query"]["evidence_type"]
                tax_id = svc_obj["query"]["tax_id"]
                query_url = "%s/%s/%s/" % (svc_obj["apiurl"], tax_id,example_id)
            elif svc_name in ["glycan_to_biosynthesis_enzymes",
                    "glycan_to_glycoproteins","glycan_to_enzyme_gene_loci",
                    "biosynthesis_enzyme_to_glycans"]:
                example_id = ""
                if "glytoucan_ac" in svc_obj["query"]:
                    example_id = svc_obj["query"]["glytoucan_ac"]
                if "uniprot_canonical_ac" in svc_obj["query"]:
                    example_id = svc_obj["query"]["uniprot_canonical_ac"]
                tax_id = svc_obj["query"]["tax_id"]
                query_url = "%s/%s/%s/" % (svc_obj["apiurl"], tax_id,example_id)
            elif "query" in svc_obj:
                query_url = "%s?query=%s" % (svc_obj["apiurl"], json.dumps(svc_obj["query"]))

            if query_url == "":
                print "STATUS: failed ... %s|empty query" % (svc_name)
                continue
            
            api_url = api_base_url + query_url
            res = requests.get(api_url, verify=False)
            if res.status_code != 200:
                print "STATUS: failed ... %s|%s" % (svc_name,api_url)
                continue
            json_obj = json.loads(res.content)
            if svc_name == "protein_search":
                protein_list_id = json_obj["list_id"]
            elif svc_name == "glycan_search":
                glycan_list_id = json_obj["list_id"]
            
            if "error_list" in json_obj:
                print "STATUS: failed ", svc_name, api_url, json_obj["error_list"]
                continue

            out_file = "tmp/example_data/%s.json" % (svc_name)
            with open(out_file, "w") as FW:
                FW.write("%s\n" % (json.dumps(json_obj, indent=4)))
            print "STATUS: success ... ", svc_name


    except Exception, e:
        print e
        print traceback.format_exc()



if __name__ == '__main__':
    main()





