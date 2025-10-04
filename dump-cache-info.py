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
    coll = "c_listcache"

    config_obj = json.loads(open("./conf/config.json", "r").read())
    #mongo_port = config_obj["dbinfo"]["port"][server]
    mongo_port = "27017"
    host = "mongodb://127.0.0.1:%s" % (mongo_port)
  
    db_obj = config_obj["dbinfo"]["glydb"]
    db_name, db_user, db_pass =  db_obj["db"], db_obj["user"], db_obj["password"]

    current_day = datetime.date.today()
    ts_format = "%Y-%m-%d"
        
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
        q = {}
        seen = {}
        for doc in dbh[coll].find({}, {"list_id":1, "glbl":1, "ts":1, "cache_info":1, "start":1}):
            if "_id" in doc:
                doc.pop("_id")
            if "list_id" not in doc:
                continue
            list_id = doc["list_id"]
            ts = doc["ts"] if coll == "c_listcache" else doc["cache_info"]["ts"]
            parts = ts.split(" ")[0].split("-")
            yy, mm, dd = parts[0], parts[1], parts[2]
            day = datetime.date(int(yy), int(mm), int(dd))
            doc_age = (current_day - day).days
            search_type, empty_search_flag = "", False
            if list_id == "9b6da20b623672f83db6060ba3fba174":
                print (json.dumps(doc, indent=4))
                exit()
            continue
            if coll == "c_cache":
                if "search_type" in doc["cache_info"]:
                    search_type = doc["cache_info"]["search_type"]
                if "empty_search_flag" in doc["cache_info"]:
                    empty_search_flag = doc["cache_info"]["empty_search_flag"]
            if search_type == "supersearch" and empty_search_flag == True:
                print ("skipping supersearch cache %s %s" % (list_id, ts))
                continue
            if search_type == "structure_search":
                print ("skipping structure_search cache %s %s" % (list_id, ts))
                continue
            print (list_id, ts, search_type)
    except pymongo.errors.ServerSelectionTimeoutError as err:
        print (err)
    except pymongo.errors.OperationFailure as err:
        print (err)



if __name__ == '__main__':
    main()
