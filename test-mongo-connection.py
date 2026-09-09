import os,sys
import json
import pymongo
from pymongo import MongoClient



###############################
def main():


    host = "mongodb://172.17.0.1:27017"
    glydb_name, db_user, db_pass =  "glydb","glydbadmin", "glydbpass"
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
        print ("success")
    except pymongo.errors.ServerSelectionTimeoutError as err:
        print (err)
    except pymongo.errors.OperationFailure as err:
        print (err)

    return



if __name__ == '__main__':
    main()
