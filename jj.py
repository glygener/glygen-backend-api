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

    jsondb_dir = config_obj["data_path"] + "/releases/data/v-%s/jsondb/" % (ver)

    dir_list = os.listdir(jsondb_dir)
    print (json.dumps(dir_list, indent=4))



if __name__ == '__main__':
    main()
