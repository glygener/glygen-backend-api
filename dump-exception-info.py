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
    parser.add_option("-i","--logid",action="store",dest="logid",help="") 
    (options,args) = parser.parse_args()

    for key in ([options.server, options.logid]):
        if not (key):
            parser.print_help()
            sys.exit(0)

    server = options.server
    log_id = options.logid


    db_name = "glydb"

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
        log_doc = dbh["c_log"].find_one({"id":log_id})
        request_doc = {} 
        if "request_id" in log_doc:
            request_id = log_doc["request_id"]
            request_doc = dbh["c_request"].find_one({"request_id":request_id})        
           
        if "_id" in log_doc:
            log_doc.pop("_id") 
        if "_id" in request_doc:
            request_doc.pop("_id")
        print (json.dumps(log_doc, indent=4))
        print ("//\n")
        print (json.dumps(request_doc, indent=4))
        print ("//\n")
 
    except pymongo.errors.ServerSelectionTimeoutError as err:
        print (err)
    except pymongo.errors.OperationFailure as err:
        print (err)



if __name__ == '__main__':
    main()
