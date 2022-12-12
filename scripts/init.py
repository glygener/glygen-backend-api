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

    db_name = "glydb"
    db_obj = { "mongodbuser":"glydbadmin", "mongodbpassword":"glydbpass"}
    db_obj["mongodbname"] = db_name

    try:
        client = pymongo.MongoClient('mongodb://running_glygen_mongo_tst:27017',
            username=db_obj["mongodbuser"],
            password=db_obj["mongodbpassword"],
            authSource=db_name,
            authMechanism='SCRAM-SHA-1',
            serverSelectionTimeoutMS=10000
        )
        client.server_info()
        dbh = client[db_name]
    except pymongo.errors.ServerSelectionTimeoutError as err:
        print (err)
    except pymongo.errors.OperationFailure as err:
        print (err)



if __name__ == '__main__':
    main()
