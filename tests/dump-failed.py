import os,sys
import string
from optparse import OptionParser
import glob
import json
from bson import json_util
import pymongo
from pymongo import MongoClient
import datetime
import pytz
import subprocess

__version__="1.0"
__status__ = "Dev"

###############################
def main():

    ignore_list = [
        "'gene_names' is a required property",
        "'publication' is a required property",
        "'summary' is a required property",
        "'description' is a required property",
        "'residue' is a required property"
    ]
    ignore_list = []
    seen = {}
    err_dict = {}
    file_list = glob.glob("/data/shared/glygen/logs/rykahsay_failure_log_protein_detail.*.json")
    for in_file in file_list:
        doc = json.loads(open(in_file, "r").read())
        main_id = in_file.split(".")[-2]
        #print (in_file)
        if "validation" in doc:
            for err in doc["validation"]["error_list"]:
                if err not in ignore_list:
                    if err not in err_dict:
                        err_dict[err] = {}
                    err_dict[err][main_id] = True

    
    #print (json.dumps(err_dict, indent=4))
    tmp_list = []
    for err in err_dict:
        tmp_list += list(err_dict[err].keys())
    print (json.dumps(tmp_list, indent=4))


if __name__ == '__main__':
    main()
