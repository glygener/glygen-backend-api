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

def get_coll_list(db_list):
    coll_list = []
    for d in db_list:
        if d[-2:] != "db":
            continue                                    
        coll = "c_" + d[:-2]
        if coll == "c_jumbo":
            continue                                                                            
        coll_list.append(coll)
    return coll_list

###############################
def main():


    usage = "\n%prog  [options]"
    parser = OptionParser(usage,version="%prog version___")
    parser.add_option("-s","--server",action="store",dest="server",help="dev/tst/beta/prd")
    parser.add_option("-v","--dataversion",action="store",dest="dataversion",help="2.0.2/2.0.3 ...")
        
    (options,args) = parser.parse_args()

    for key in ([options.server, options.dataversion]):
        if not (key):
            parser.print_help()
            sys.exit(0)

    server = options.server
    ver = options.dataversion
    mode = "full"

    config_obj = json.loads(open("./conf/config.json", "r").read())
    mongo_port = config_obj["dbinfo"]["port"][server]
    host = "mongodb://127.0.0.1:%s" % (mongo_port)

    jsondb_dir = config_obj["data_path"] + "/releases/data/v-%s/jsondb/" % (ver)
    dump_dir = config_obj["data_path"] + "/mongodump/"

    db_list = config_obj["downloads"]["jsondb"]
    coll_list = get_coll_list(db_list)

    print (coll_list)


if __name__ == '__main__':
    main()
