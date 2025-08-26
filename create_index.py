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
    mongo_port = "27017"
    host = "mongodb://127.0.0.1:%s" % (mongo_port)

    db_name = "glydb_beta" if server == "beta" else "glydb"
    db_obj = config_obj["dbinfo"][db_name]
    glydb_name, db_user, db_pass =  db_obj["db"], db_obj["user"], db_obj["password"]


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
        

        #res = dbh[coll].create_index([("$**", pymongo.TEXT)])
        path = "phraselist"
        index_name = "phraselist_index"
        #res = dbh[coll].create_index([(path, -1 )], name=index_name)
        #res = dbh[coll].drop_index(index_name)

        for cur in dbh[coll].list_indexes():
            print(f"Index Name: {cur['name']}")

    except pymongo.errors.ServerSelectionTimeoutError as err:
        print (err)
    except pymongo.errors.OperationFailure as err:
        print (err)



if __name__ == '__main__':
    main()
