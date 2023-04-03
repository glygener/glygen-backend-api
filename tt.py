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


def get_first_batch(dbh, record_type, record_id):
    
    q = {
        "$and":[
            {"batchid":{"$eq":1}}, 
            {"recordid": {"$regex":record_id, "$options":"i"}},
            {"recordtype":{"$eq":record_type}}
        ]
    }
    doc = dbh["c_batch"].find_one(q)
    
    return {} if doc == None else doc["sections"] 


###############################
def main():


    server = "tst"
    coll = "c_batch"

    config_obj = json.loads(open("./conf/config.json", "r").read())
    mongo_port = config_obj["dbinfo"]["port"][server]
    mongo_container = "running_glygen_mongo_%s" % (server)

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
        
        record_type, record_id = "publication", "pubmed.17081983"
        record_type, record_id = "glycan", "G49108TOX"
        record_type, record_id = "protein", "P04637"

        sec_dict = get_first_batch(dbh, record_type, record_id)
        print (json.dumps(sec_dict, indent=4))

    except pymongo.errors.ServerSelectionTimeoutError as err:
        print (err)
    except pymongo.errors.OperationFailure as err:
        print (err)



if __name__ == '__main__':
    main()
