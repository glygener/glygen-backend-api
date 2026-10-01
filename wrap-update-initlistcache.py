import os,sys
import string
import pytz
import datetime
import glob
import json
import subprocess
from lib_update import get_mongodb
from optparse import OptionParser
from cacheutil import get_c_initlistcache_queries



def main():

    
    usage = "\n%prog  [options]"
    parser = OptionParser(usage,version="%prog version___")
    parser.add_option("-s","--server",action="store",dest="server",help="dev/tst/beta/prd")
    parser.add_option("-r","--recordtype",action="store",dest="recordtype",help="protein/gycan/...")
    
    
    (options,args) = parser.parse_args()
    for key in ([options.server]):
        if not (key):
            parser.print_help()
            sys.exit(0)
                                         
    server = options.server
    record_type = options.recordtype

    db_name = "glydb"
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


    query_doc = get_c_initlistcache_queries(dbh, config_obj)
    for r_type in query_doc:
        for cache_name in query_doc[r_type]:
            if record_type != None and cache_name.find(record_type) == -1:
                continue
            cmd = "python3 update-initlistcache.py -s %s -n %s" % (server, cache_name)
            x = subprocess.getoutput(cmd)
            #print ("finished ...", cmd)


    return


if __name__ == '__main__':
    main()
