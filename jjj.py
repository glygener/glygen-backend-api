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

def write_progress_msg(msg, flag):
    ts = datetime.datetime.now()
    with open("logs/data_loading_progress.txt", flag) as F:
        F.write("%s [%s]\n" % (msg, ts))
    return

            

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


    tmpdb_user = config_obj["dbinfo"]["tmpdb"]["user"]
    tmpdb_pass = config_obj["dbinfo"]["tmpdb"]["password"]
    tmpdb_name =  config_obj["dbinfo"]["tmpdb"]["db"] 
    
    db_user = config_obj["dbinfo"]["glydb"]["user"]
    db_pass = config_obj["dbinfo"]["glydb"]["password"]
    db_name =  config_obj["dbinfo"]["glydb"]["db"]
    indexed_colls = ["c_protein", "c_glycan"]


    jsondb_dir = config_obj["data_path"] + "/releases/data/v-%s/jsondb/" % (ver)
    dump_dir = config_obj["data_path"] + "/mongodump/"


    dir_list = os.listdir(jsondb_dir)
    dir_list.remove("proteindb")
    dir_list.remove("glycandb")
    dir_list = ["glycandb", "proteindb"] + dir_list


    # NOW CLEARING DUMP DIR
    cmd = "docker exec running_glygen_mongo_%s rm -rf %s/tmpdb " % (server, dump_dir)
    x = subprocess.getoutput(cmd)
    
    cmd = "docker exec running_glygen_mongo_%s mongodump --username %s --password %s "
    cmd += "--db tmpdb --out %s"
    cmd = cmd % (server, tmpdb_user, tmpdb_pass, dump_dir)
    x = subprocess.getoutput(cmd)
    print (x)

    cmd = "docker exec running_glygen_mongo_%s "
    cmd += "mongorestore --username %s --password %s --db %s "
    cmd += "%s/tmpdb --drop"
    cmd = cmd % (server, db_user, db_pass, db_name, dump_dir)
    x = subprocess.getoutput(cmd)






if __name__ == '__main__':
    main()
