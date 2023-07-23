import os,sys
import string
from optparse import OptionParser
import glob
import json
from bson import json_util
import pymongo
from pymongo import MongoClient
import base64
import datetime
import pytz

__version__="1.0"
__status__ = "Dev"



###############################
def main():


    usage = "\n%prog  [options]"
    parser = OptionParser(usage,version="%prog version___")
    parser.add_option("-s","--srv",action="store",dest="srv",help="dev/tst/beta/prd")
        
    (options,args) = parser.parse_args()

    for key in ([options.srv]):
        if not (key):
            parser.print_help()
            sys.exit(0)

    srv = options.srv


    config_obj = json.loads(open("./conf/config.json", "r").read())
    mongo_port = config_obj["dbinfo"]["port"][srv]
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
        coll = "c_video"
        url = "https://www.youtube.com/watch?v=W13gi7nVCWc"
        res = dbh[coll].delete_many({})
        obj = {"url":url}
        obj["createdts"] = datetime.datetime.now()
        obj["visibility"] = "visible"

        res = dbh[coll].insert_one(obj)
    except pymongo.errors.ServerSelectionTimeoutError as err:
        print (err)
    except pymongo.errors.OperationFailure as err:
        print (err)



if __name__ == '__main__':
    main()
