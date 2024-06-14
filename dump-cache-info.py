import os,sys
import string
from optparse import OptionParser
import glob
import json
from bson import json_util
import pymongo
from pymongo import MongoClient
import datetime


__version__="1.0"
__status__ = "Dev"



###############################
def main():


    usage = "\n%prog  [options]"
    parser = OptionParser(usage,version="%prog version___")
    parser.add_option("-s","--server",action="store",dest="server",help="dev/tst/beta/prd")
    parser.add_option("-c","--coll",action="store",dest="coll",help="") 

    (options,args) = parser.parse_args()

    for key in ([options.server, options.coll ]):
        if not (key):
            parser.print_help()
            sys.exit(0)

    server = options.server
    coll = options.coll

    config_obj = json.loads(open("./conf/config.json", "r").read())
    #mongo_port = config_obj["dbinfo"]["port"][server]
    mongo_port = "27017"
    host = "mongodb://127.0.0.1:%s" % (mongo_port)
  
    db_obj = config_obj["dbinfo"]["glydb"]
    db_name, db_user, db_pass =  db_obj["db"], db_obj["user"], db_obj["password"]

    try:
        client = pymongo.MongoClient(host,
            username=db_user,
            password=db_pass,
            authSource=db_name,
            authMechanism='SCRAM-SHA-1',
            serverSelectionTimeoutMS=10000
        )
        client.server_info()
        dbh = client[db_name]
        q = {}
        seen = {}
        for doc in dbh[coll].find(q):
            list_id = doc["list_id"]
            doc = doc["res"] if coll in ["c_listcache"] else doc
            k_one = "cache_info"
            tmp_dict = {"ts":"xxx", "search_type":"xxx", "record_type":"xxx"}
            if k_one in doc:
                for k in tmp_dict:
                    if k in doc[k_one]:
                        tmp_dict[k] = doc[k_one][k]
            if list_id not in seen:
                print (list_id, tmp_dict["ts"], tmp_dict["record_type"], tmp_dict["search_type"])
                seen[list_id] = True
    except pymongo.errors.ServerSelectionTimeoutError as err:
        print (err)
    except pymongo.errors.OperationFailure as err:
        print (err)



if __name__ == '__main__':
    main()
