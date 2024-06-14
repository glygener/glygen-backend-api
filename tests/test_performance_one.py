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
    parser.add_option("-s","--server",action="store",dest="server",help="dev/tst/beta/prd")
    parser.add_option("-g","--group",action="store",dest="group",help="all/protein/glycan/...")
    parser.add_option("-a","--apiname",action="store",dest="apiname",help="")
    

    (options,args) = parser.parse_args()
    for key in ([options.server, options.group, options.apiname]):
        if not (key):
            parser.print_help()
            sys.exit(0)

    server = options.server
    api_grp = options.group
    api_name = options.apiname

    config_obj = json.loads(open("../conf/config.json", "r").read())
    test_lib.run_performance_test(api_name, api_grp, config_obj, server)

    return






if __name__ == '__main__':
    main()





