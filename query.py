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
    mongo_port = config_obj["dbinfo"]["port"][server]
    mongo_container = "running_glygen_mongo_%s" % (server)

    db_obj = config_obj["dbinfo"]["glydb"]
    db_name, db_user, db_pass =  db_obj["db"], db_obj["user"], db_obj["password"]


    host = "mongodb://127.0.0.1:%s" % (mongo_port)

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
        term = "kinase" 
        #term = "P14210"
        q = {}
        q = {"$text": {"$search": term}}
        q = {"function":{"$regex":term, "$options":"i"}}
        q = {
                "$and":[
                    {"$or":[
                        {"protein_names.name":{"$regex":term, "$options": "i"}},
                        {"refseq.name":{"$regex":term, "$options": "i"}}
                    ]
                    },
                    {"glycosylation": {"$gt":[]}}
                ]
        }
        q = {"$text": {"$search": term}}
        tmp_list = list(dbh[coll].find(q, {"uniprot_canonical_ac":-1}))
        print (len(tmp_list))
        exit()
        for doc in dbh[coll].find(q, {"_id":-1}).limit(1000000):
            print (doc["_id"])
        exit()
        #q = {}
        for doc in dbh[coll].find(q):
            for p in ["_id", "password"]:
                if p in doc:
                    doc.pop(p)
            print (json.dumps(doc, indent=4))
    except pymongo.errors.ServerSelectionTimeoutError as err:
        print (err)
    except pymongo.errors.OperationFailure as err:
        print (err)



if __name__ == '__main__':
    main()
