import sys,os
import json
import string
import csv
import traceback
import requests
from optparse import OptionParser
import pymongo
from pymongo import MongoClient


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
        res_obj = {}
        # call this and get json as res_obj
        url = "http://localhost:8082/supersearch/search/"
        req_obj = json.loads(open("conf/init_query.json", "r").read())

        res = requests.post(url, json=req_obj, allow_redirects=True)
        res_obj = json.loads(res.content)
        q_obj = {}
        update_obj = {"supersearch_init":res_obj["results_summary"]}
        res = dbh["c_searchinit"].update_one(q_obj, {'$set':update_obj}, upsert=True)
    except pymongo.errors.ServerSelectionTimeoutError as err:
        print (err)
    except pymongo.errors.OperationFailure as err:
        print (err)





if __name__ == '__main__':
    main()





