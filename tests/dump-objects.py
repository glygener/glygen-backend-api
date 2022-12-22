import os,sys
import string
from optparse import OptionParser
import glob
from bson import json_util, ObjectId
import json
import pymongo
from pymongo import MongoClient
import datetime


__version__="1.0"
__status__ = "Dev"



def connect_to_mongodb(db_obj):

    try:
        client = pymongo.MongoClient('mongodb://localhost:27017',
            username=db_obj["mongodbuser"],
            password=db_obj["mongodbpassword"],
            authSource=db_obj["mongodbname"],
            authMechanism='SCRAM-SHA-1',
            serverSelectionTimeoutMS=10000
        )
        client.server_info()
        dbh = client[db_obj["mongodbname"]]
        return dbh, {}
    except pymongo.errors.ServerSelectionTimeoutError as err:
        return {}, {"error_list":[{"error_code": "open-connection-failed"}]}
    except pymongo.errors.OperationFailure as err:
        return {}, {"error_list":[{"error_code": "mongodb-auth-failed"}]}





###############################
def main():

    usage = "\n%prog  [options]"
    parser = OptionParser(usage,version="%prog version___")
    parser.add_option("-c","--coll",action="store",dest="coll",help="SVC name")
    (options,args) = parser.parse_args()
    for key in ([options.coll]):
        if not (key):
            parser.print_help()
            sys.exit(0)
                                         
    coll = options.coll

    config_obj = json.loads(open("./conf/config.json", "r").read())
    #config_obj["server"] = "beta"
    path_obj  =  config_obj[config_obj["server"]]["pathinfo"]
    db_obj = config_obj[config_obj["server"]]["dbinfo"]

    dbh, error_obj = connect_to_mongodb(db_obj) #connect to mongodb
    if error_obj != {}:
        print (error_obj)
        sys.exit()

    #q_obj = {"email":"rykahsay@gwu.edu"}
    #update_obj = {"status":1, "access":"write", "role":"admin"}
    #res = dbh[coll].update_one(q_obj, {'$set':update_obj}, upsert=True)
    #res = dbh[coll].delete_many({})
    
    
    query_obj = {}
    for doc in dbh[coll].find(query_obj):
        doc["_id"] = str(doc["_id"])
        #for k in ["ts", "createdts", "creation_time", "update_time", "start_date","end_date"]:
            #if k in doc:
            #    doc[k] = doc[k].strftime('%Y-%m-%d %H:%M:%S %Z%z')
        print (json.dumps(doc, indent=4, default=json_util.default))


if __name__ == '__main__':
	main()


