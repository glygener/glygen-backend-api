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
    parser.add_option("-m","--mode",action="store",dest="mode",help="1 (using example queries), 2 (exhaustive detail API calls)")
    parser.add_option("-g","--group",action="store",dest="group",help="all/protein/glycan/...")
        

    (options,args) = parser.parse_args()
    for key in ([options.group, options.mode]):
        if not (key):
            parser.print_help()
            sys.exit(0)

    api_grp = options.group
    mode = int(options.mode)

    global config_obj
    global user_name
    global jsondb_dir
    global log_dir

    config_obj = json.loads(open("../conf/config.json", "r").read())
    user_name = os.getlogin()
   
    api_url = config_obj["base_url"] + "/misc/info"
    res = requests.post(api_url, json={}, verify=False)
    info_obj =  json.loads(res.content)
    data_version = info_obj["initobj"]["dataversion"]
    jsondb_dir = config_obj["data_path"] + "releases/data/v-%s/jsondb/" % (data_version)
    log_dir = config_obj["data_path"]  + "/logs/"


    if mode == 2:
        #record_type_list = ["glycan", "protein"]
        record_type_list = ["protein"]
        for record_type in record_type_list:
            cmd = "rm -f " + log_dir + "failure_log_%s_detail.*" % (record_type)
            x = subprocess.getoutput(cmd)
            file_list = glob.glob(jsondb_dir + "testdb/%s.*.json" % (record_type))
            for in_file in sorted(file_list):
                test_lib.run_exhaustive(in_file, record_type, config_obj)
    else:
        test_lib.run_from_queries(api_grp, config_obj)

    return






if __name__ == '__main__':
    main()





