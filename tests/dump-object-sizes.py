import sys,os
import json
import string
import traceback
from optparse import OptionParser
import requests
import glob
import subprocess
import test_lib




def main():
   
    usage = "\n%prog  [options]"
    parser = OptionParser(usage,version="%prog version___")
    parser.add_option("-r","--recordtype",action="store",dest="recordtype",help="protein/glycan/...")
    
    (options,args) = parser.parse_args()
    for key in ([options.recordtype]):
        if not (key):
            parser.print_help()
            sys.exit(0)

    record_type = options.recordtype

    global config_obj
    global jsondb_dir
    global log_dir

    config_obj = json.loads(open("../conf/config.json", "r").read())
  

    cmd = "ls -lS /data/shared/glygen/releases/data/v-2.5.1/jsondb/%sdb/ | grep json" % (record_type)
    line_list = subprocess.getoutput(cmd).split("\n")[:3]
    for line in line_list:
        print (line)

    return






if __name__ == '__main__':
    main()





