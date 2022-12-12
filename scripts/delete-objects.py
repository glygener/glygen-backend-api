import os,sys
import string
from optparse import OptionParser
import glob
import json
import pymongo
from pymongo import MongoClient


__version__="1.0"
__status__ = "Dev"



###############################
def main():

    usage = "\n%prog  [options]"
    parser = OptionParser(usage,version="%prog version___")
    parser.add_option("-d","--dbname",action="store",dest="dbname",help="Database")
    parser.add_option("-c","--coll",action="store",dest="coll",help="Collection")
    parser.add_option("-v","--ver",action="store",dest="ver",help="Release version")

    (options,args) = parser.parse_args()
    for key in ([options.dbname, options.coll, options.ver]):
        if not (key):
            parser.print_help()
            sys.exit(0)

    db_name = options.dbname
    coll = options.coll
    ver = options.ver
    
    db_obj = { "mongodbuser":"%sadmin" % (db_name), 
        "mongodbpassword":"%spass" % (db_name)}
    
    db_obj["mongodbname"] = db_name
    
    if coll in ["c_bco", "c_history", "c_extract"]:
        coll = "%s_v-%s" % (coll, ver)

    try:
        client = pymongo.MongoClient('mongodb://running_mongo_tst:27017',
                username=db_obj["mongodbuser"],
                password=db_obj["mongodbpassword"],
                authSource=db_obj["mongodbname"],
                authMechanism='SCRAM-SHA-1',
                serverSelectionTimeoutMS=10000
        )
        client.server_info()
        dbh = client[db_obj["mongodbname"]]
        result = dbh[coll].delete_many({})
    except pymongo.errors.ServerSelectionTimeoutError as err:
        print (err)
    except pymongo.errors.OperationFailure as err:
        print (err)



if __name__ == '__main__':
	main()
