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

    for key in ([options.server, options.coll]):
        if not (key):
            parser.print_help()
            sys.exit(0)

    server = options.server
    coll = options.coll

    config_obj = json.loads(open("./conf/config.json", "r").read())
    #mongo_port = config_obj["dbinfo"]["port"][server]
    mongo_port = "27017"
    
    host = "mongodb://127.0.0.1:%s" % (mongo_port)
  
    db_name = "glydb_beta" if server == "beta" else "glydb"
    db_obj = config_obj["dbinfo"][db_name]
    glydb_name, db_user, db_pass =  db_obj["db"], db_obj["user"], db_obj["password"]

    try:
        client = pymongo.MongoClient(host,
            username=db_user,
            password=db_pass,
            authSource=glydb_name,
            authMechanism='SCRAM-SHA-1',
            serverSelectionTimeoutMS=10000
        )
        client.server_info()
        dbh = client[db_name]
        for doc in dbh[coll].find({}):
            empty_search_flag, search_type = False, ""
            if "cache_info" in doc:
                if "empty_search_flag" in doc["cache_info"]:
                    empty_search_flag = doc["cache_info"]["empty_search_flag"]
                if "search_type" in doc["cache_info"]:
                    search_type = doc["cache_info"]["search_type"]
            if search_type == "supersearch" and empty_search_flag == True:
                continue
            if search_type == "structure_search":
                continue
            list_id = doc["list_id"]
            res = dbh[coll].delete_many({"list_id":list_id})
            print ("deleted:", list_id)

    except pymongo.errors.ServerSelectionTimeoutError as err:
        print (err)
    except pymongo.errors.OperationFailure as err:
        print (err)



if __name__ == '__main__':
    main()
