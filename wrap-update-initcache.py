import os,sys
import string
import pytz
import datetime
import glob
import json
import subprocess
from lib_update import get_mongodb
from optparse import OptionParser
from cacheutil import get_c_initcache_queries,get_supersearch_init_query, get_pulldown_dict



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


    db_name = "glydb_beta" if server == "beta" else "glydb"
    config_obj = json.loads(open("./conf/config.json", "r").read())
    db_obj = config_obj["dbinfo"][db_name]
    glydb_name, db_user, db_pass =  db_obj["db"], db_obj["user"], db_obj["password"]
    host_ip = config_obj["host_ip"][server]
    config_obj = json.load(open("glygen/conf/config.json"))
    config_obj["db_info"] = {"user":db_user, "password":db_pass, "host_ip":host_ip, "db_name":db_name}
           
    
    dbh, error_obj = get_mongodb(config_obj["db_info"])
    if error_obj != {}:
        print (error_obj)
        exit()

    pulldown_dict = get_pulldown_dict(dbh, config_obj)
    query_doc = get_supersearch_init_query(dbh, config_obj, pulldown_dict) 
    #print (json.dumps(query_doc, indent=4))
    for record_type in query_doc:
        for cache_name in query_doc[record_type]:
            cmd = "python3 update-initcache.py -s %s -n %s" % (server, cache_name)
            #x = subprocess.getoutput(cmd)
            print (cache_name)
    query_doc = get_c_initcache_queries(dbh, config_obj, pulldown_dict)
    for record_type in query_doc:
        for cache_name in query_doc[record_type]:
            cmd = "python3 update-initcache.py -s %s -n %s" % (server, cache_name)
            #x = subprocess.getoutput(cmd)
            print (cache_name)

 

    return


if __name__ == '__main__':
    main()
