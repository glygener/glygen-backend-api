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

    (options,args) = parser.parse_args()
    for key in ([options.server]):
        if not (key):
            parser.print_help()
            sys.exit(0)

    server = options.server
    record_type = "protein"

    global config_obj
    global jsondb_dir
    global log_dir

    config_obj = json.loads(open("../conf/config.json", "r").read())
   
    api_url = config_obj["base_url"][server] +  "/misc/info"
    res = requests.post(api_url, json={}, verify=False)
    info_obj =  json.loads(res.content)
    data_version = info_obj["initobj"]["dataversion"]
    jsondb_dir = config_obj["data_path"] + "releases/data/v-%s/jsondb/" % (data_version)
    log_dir = config_obj["data_path"]  + "/logs/"

    in_file = "FAILED.json"
    if os.path.isfile(in_file):
        cmd = "rm -f " + log_dir + "failure_log_%s_detail.*" % (record_type)
        x = subprocess.getoutput(cmd)
        test_lib.run_exhaustive(in_file, record_type, config_obj, server)

    return






if __name__ == '__main__':
    main()





