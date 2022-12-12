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
    parser.add_option("-v","--dataversion",action="store",dest="dataversion",help="2.0.2/2.0.3 ...")
    (options,args) = parser.parse_args()
    for key in ([options.dataversion]):
        if not (key):
            parser.print_help()
            sys.exit(0)

    ver = options.dataversion

    config_obj = json.loads(open("./conf/config.json", "r").read())
    mongo_port = config_obj["dbinfo"]["port"]
    host = "mongodb://127.0.0.1:%s" % (mongo_port)

    jsondb_dir = config_obj["data_path"] + "/releases/data/v-%s/jsondb/" % (ver)

    dir_list = os.listdir(jsondb_dir)

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
        for d in dir_list:
            if d[-2:] != "db":
                continue
            coll = "c_" + d[:-2]
            n = dbh[coll].count_documents({})
            if n > 0:
                result = dbh[coll].delete_many({})
                print (" ... deleted %s records from %s" % (n, coll))
    except pymongo.errors.ServerSelectionTimeoutError as err:
        print (err)
    except pymongo.errors.OperationFailure as err:
        print (err)



if __name__ == '__main__':
    main()
