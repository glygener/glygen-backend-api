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
    parser.add_option("-b","--batch",action="store",dest="batch",help="1/2/3")
    
    (options,args) = parser.parse_args()
    for key in ([options.recordtype, options.batch]):
        if not (key):
            parser.print_help()
            sys.exit(0)

    record_type = options.recordtype
    batch = options.batch

    global config_obj
    global jsondb_dir
    global log_dir

    config_obj = json.loads(open("../conf/config.json", "r").read())
   
    api_url = config_obj["base_url"] + "/misc/info"
    res = requests.post(api_url, json={}, verify=False)
    info_obj =  json.loads(res.content)
    data_version = info_obj["initobj"]["dataversion"]
    jsondb_dir = config_obj["data_path"] + "releases/data/v-%s/jsondb/" % (data_version)
    log_dir = config_obj["data_path"]  + "/logs/"

    in_file = jsondb_dir + "testdb/%s.batch.%s.json" % (record_type, batch)
    if os.path.isfile(in_file):
        cmd = "rm -f " + log_dir + "failure_log_%s_detail.*" % (record_type)
        x = subprocess.getoutput(cmd)
        test_lib.run_exhaustive(in_file, record_type, config_obj)

    return






if __name__ == '__main__':
    main()





