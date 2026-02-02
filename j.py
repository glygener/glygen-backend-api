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

    score = 0.1
    doc = json.load(open("junk"))
    for obj in doc:
        score += obj["w"] + round(float(obj["f"])/100.00,3)
        print (obj)
    print (score)
    exit()
 
    doc = json.load(open("glygen/conf/section.json"))
    for sec in doc["site"]:
        for obj in doc["site"][sec]["fieldmap"]:
            if obj["path"] in ["start_pos","end_pos"]:
                print (sec, obj)
    exit()


    server = "beta"
    coll = "c_index"

    db_name = "glydb_beta" if server == "beta" else "glydb"

    config_obj = json.loads(open("./conf/config.json", "r").read())
    #mongo_port = config_obj["dbinfo"]["port"][server]
    mongo_port = "27017"
    host = "mongodb://127.0.0.1:%s" % (mongo_port)
  
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
        dbh = client[glydb_name]
        prj_obj = {"record_type":1, "record_id":1, "section":1}
        #qry_obj = {"phraselist":{"$eq":"hgf"}, "record_type":{"$eq":"protein"}}
        qry_obj = {"phraselist": {"$eq": "glycosylation"},"record_type": {"$eq": "site"}}
        qry_obj = {"record_type": {"$eq": "site"}} 
        for doc in dbh["c_index"].find(qry_obj, prj_obj).limit(10):
            print (doc)

    except pymongo.errors.ServerSelectionTimeoutError as err:
        print (err)
    except pymongo.errors.OperationFailure as err:
        print (err)



if __name__ == '__main__':
    main()
