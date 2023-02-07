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
    (options,args) = parser.parse_args()

    for key in ([options.server]):
        if not (key):
            parser.print_help()
            sys.exit(0)

    server = options.server


    config_obj = json.loads(open("./conf/config.json", "r").read())
    mongo_port = config_obj["dbinfo"]["port"][server]
    host = "mongodb://127.0.0.1:%s" % (mongo_port)

    glydb_user, glydb_pass = config_obj["dbinfo"]["glydb"]["user"], config_obj["dbinfo"]["glydb"]["password"]
    glydb_db =  config_obj["dbinfo"]["glydb"]["db"]

    try:
        client = pymongo.MongoClient(host,
            username=glydb_user,
            password=glydb_pass,
            authSource=glydb_db,
            authMechanism='SCRAM-SHA-1',
            serverSelectionTimeoutMS=10000
        )
        client.server_info()
        dbh = client[glydb_db]
        
        for coll in ["c_glycan", "c_protein"]:
            res = dbh[coll].create_index([("$**", pymongo.TEXT)])

    except pymongo.errors.ServerSelectionTimeoutError as err:
        print (err)
    except pymongo.errors.OperationFailure as err:
        print (err)



if __name__ == '__main__':
    main()
