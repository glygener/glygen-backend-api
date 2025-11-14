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



    server = "tst"
    coll = "c_initcache"

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
            authSource=glydb_name,
            authMechanism='SCRAM-SHA-1',
            serverSelectionTimeoutMS=10000
        )
        client.server_info()
        dbh = client[db_name]
        seen = {}
        cache_id_list = json.load(open("tmp/junk.json"))
        for cache_id in cache_id_list:
            q_obj = {"list_id":cache_id}
            res = dbh[coll].delete_many(q_obj)
            print ("deleted ", cache_id)

    except pymongo.errors.ServerSelectionTimeoutError as err:
        print (err)
    except pymongo.errors.OperationFailure as err:
        print (err)



if __name__ == '__main__':
    main()
