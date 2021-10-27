import sys,os
import json
import string
import csv
import traceback
from optparse import OptionParser

from protein_apilib import protein_detail, protein_alignment, protein_search, protein_search_simple,protein_list, protein_search_init

from glycan_apilib import glycan_detail, glycan_search, glycan_search_simple,glycan_list,glycan_search_init

import errorlib
import util

import jsonref
from jsonschema import validate, Draft4Validator

import jsonschema
import simplejson

def main():

    global config_obj
    global path_obj
    config_obj = json.loads(open("./conf/config.json", "r").read())
    path_obj  =  config_obj[config_obj["server"]]["pathinfo"]
    db_obj = config_obj[config_obj["server"]]["dbinfo"]


    try:
        svc_obj_list = simplejson.loads(open("conf/validation.conf", "r").read())
        for svc_obj in svc_obj_list:
            svc_name = svc_obj["svc"]
            data_file = "specs/example_data/%s.json" % (svc_name)
            schema_file = svc_obj["schemafile"]
            msg_list = []
            if os.path.isfile(data_file) == False:
                msg  = "file doesn't exist:%s" % (data_file)
                msg_list.append(msg)
            elif os.path.isfile(schema_file) == False:            
                msg = "file doesn't exist:%s" % (schema_file)
                msg_list.append(msg)
            else:
                base_uri = 'file://{}/'.format(os.path.dirname(schema_file))
                schema_obj = jsonref.load(open(schema_file, 'r'), base_uri=base_uri, jsonschema=True)
                #resolver = jsonschema.RefResolver(schema_file, None)
                #schema_obj = simplejson.loads(open(schema_file, "r").read())
            
                json_obj = simplejson.loads(open(data_file, "r").read())
                v = Draft4Validator(schema_obj)
                error_list = sorted(v.iter_errors(json_obj), key=str)
                flag = "failed" if len(error_list) > 0 else "passed"
                for error in error_list:
                    msg_list.append(error.message)
           
            if msg_list == []:
                print "passed", svc_name
            else:
                print "failed", svc_name, msg_list


            #res = validate(json_obj, schema_obj)
            #print res
    except Exception, e:
        print e
        print traceback.format_exc()



if __name__ == '__main__':
    main()





