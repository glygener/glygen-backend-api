import os,sys
import string
from optparse import OptionParser
import glob
import json
import pymongo
from pymongo import MongoClient
import datetime


__version__="1.0"
__status__ = "Dev"



###############################
def main():

    config_obj = json.loads(open("./conf/config.json", "r").read())
    mongo_port = config_obj["dbinfo"]["port"]
    host = "mongodb://127.0.0.1:%s" % (mongo_port)
    
    glydb_user, glydb_pass = config_obj["dbinfo"]["glydb"]["user"], config_obj["dbinfo"]["glydb"]["password"]
    glydb_db =  config_obj["dbinfo"]["glydb"]["db"]

    try:
        
        client_two = pymongo.MongoClient(host,
            username=glydb_user,
            password=glydb_pass,
            authSource=glydb_db,
            authMechanism='SCRAM-SHA-1',
            serverSelectionTimeoutMS=10000
        )
        client_two.server_info()
        dbh = client_two[glydb_db]
        for c in ["c_cache", "c_users", "c_video", "c_event"]:
            res = dbh[c]
        for c in dbh.list_collection_names():
            print (c)

    except pymongo.errors.ServerSelectionTimeoutError as err:
        print (err)
    except pymongo.errors.OperationFailure as err:
        print (err)


if __name__ == '__main__':
    main()
