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

    if coll in ["c_bco", "c_history", "c_extract"]:
        coll = "%s_v-%s" % (coll, ver)

    db_obj = { "mongodbuser":"glydbadmin", "mongodbpassword":"glydbpass"}
    db_obj["mongodbname"] = db_name
    db_path = "/data/shared/glygen/releases/data/v-%s/jsondb/" % (ver)
    file_list = glob.glob(db_path + "%sdb/*.json" % (coll.replace("c_","")))


    try:
        client = pymongo.MongoClient('mongodb://running_mongo_tst:27017',
            username=db_obj["mongodbuser"],
            password=db_obj["mongodbpassword"],
            authSource=db_name,
            authMechanism='SCRAM-SHA-1',
            serverSelectionTimeoutMS=10000
        )
        client.server_info()
        dbh = client[db_name]
        nrecords = 0
        for in_file in file_list:
            doc = json.loads(open(in_file, "r").read())
            if "_id" in doc:
                doc.pop("_id")
            result = dbh[coll].insert_one(doc)     
            nrecords += 1
            if nrecords != 0 and nrecords%1000 == 0:
                ts = datetime.datetime.now()
                print (" ... loaded %s documents to %s [%s]" % (nrecords, coll, ts))
        ts = datetime.datetime.now()
        print (" ... loaded %s documents to %s [%s]" % (nrecords, coll, ts))
    except pymongo.errors.ServerSelectionTimeoutError as err:
        print (err)
    except pymongo.errors.OperationFailure as err:
        print (err)



if __name__ == '__main__':
    main()
