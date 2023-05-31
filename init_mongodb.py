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
    host = "mongodb://127.0.0.1:%s" % (mongo_port)
    
    admin_user, admin_pass = config_obj["dbinfo"]["admin"]["user"], config_obj["dbinfo"]["admin"]["password"]
    admin_db = config_obj["dbinfo"]["admin"]["db"]

    glydb_user, glydb_pass = config_obj["dbinfo"]["glydb"]["user"], config_obj["dbinfo"]["glydb"]["password"]
    glydb_db =  config_obj["dbinfo"]["glydb"]["db"]


    try:
        client_one = pymongo.MongoClient(host,
            username=admin_user,
            password=admin_pass,
            authSource=admin_db,
            authMechanism='SCRAM-SHA-1',
            serverSelectionTimeoutMS=10000
        )
        client_one.server_info()

        #create user for glydb
        client_one.glydb.command('createUser', glydb_user, pwd=glydb_pass, 
            roles=[{'role': 'readWrite', 'db': glydb_db}])
        
        #create user for tmpdb
        client_one.tmpdb.command('createUser', glydb_user, pwd=glydb_pass, 
            roles=[{'role': 'readWrite', 'db': 'tmpdb'}])

        client_two = pymongo.MongoClient(host,
            username=glydb_user,
            password=glydb_pass,
            authSource=glydb_db,
            authMechanism='SCRAM-SHA-1',
            serverSelectionTimeoutMS=10000
        )
        client_two.server_info()
        dbh = client_two[glydb_db]
        for c in ["c_cache", "c_users", "c_video", "c_event", "c_message", "c_userid", "c_version", "c_userlog"]:
            res = dbh[c].insert_one({})
    
    except pymongo.errors.ServerSelectionTimeoutError as err:
        print (err)
    except pymongo.errors.OperationFailure as err:
        print (err)


if __name__ == '__main__':
    main()
