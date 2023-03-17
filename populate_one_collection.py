import os,sys
import string
from optparse import OptionParser
import glob
import json
from bson import json_util
import pymongo
from pymongo import MongoClient
import datetime
import pytz
import subprocess

__version__="1.0"
__status__ = "Dev"

def write_progress_msg(msg, flag):
    ts = datetime.datetime.now()
    with open(log_file,  flag) as F:
        F.write("%s [%s]\n" % (msg, ts))
    return

            

###############################
def main():


    usage = "\n%prog  [options]"
    parser = OptionParser(usage,version="%prog version___")
    parser.add_option("-s","--server",action="store",dest="server",help="dev/tst/beta/prd")
    parser.add_option("-v","--dataversion",action="store",dest="dataversion",help="2.0.2/2.0.3 ...")
    parser.add_option("-c","--coll",action="store",dest="coll",help="c_glycan/c_protein")
        
    (options,args) = parser.parse_args()

    for key in ([options.server, options.dataversion, options.coll]):
        if not (key):
            parser.print_help()
            sys.exit(0)

    global log_file

    server = options.server
    ver = options.dataversion
    coll = options.coll


    
    db = coll[2:] + "db"
    dir_list = [db]
    log_file = "logs/%s_loading_progress.txt" % (coll)


    config_obj = json.loads(open("./conf/config.json", "r").read())
    mongo_port = config_obj["dbinfo"]["port"][server]
    host = "mongodb://127.0.0.1:%s" % (mongo_port)

    jsondb_dir = config_obj["data_path"] + "/releases/data/v-%s/jsondb/" % (ver)
    
    dump_dir = config_obj["data_path"] + "/mongodump/"


    tmpdb_user = config_obj["dbinfo"]["tmpdb"]["user"]
    tmpdb_pass = config_obj["dbinfo"]["tmpdb"]["password"]
    tmpdb_name =  config_obj["dbinfo"]["tmpdb"]["db"] 
    
    glydb_user = config_obj["dbinfo"]["glydb"]["user"]
    glydb_pass = config_obj["dbinfo"]["glydb"]["password"]
    glydb_name =  config_obj["dbinfo"]["glydb"]["db"]
    indexed_colls = ["c_protein", "c_glycan"]


    msg = "\n ... started loading %s.%s version %s" % (glydb_name, coll, ver)
    write_progress_msg(msg, "w")


    try:
        tmpdb_client = pymongo.MongoClient(host,
            username=tmpdb_user,
            password=tmpdb_pass,
            authSource=tmpdb_name,
            authMechanism='SCRAM-SHA-1',
            serverSelectionTimeoutMS=10000
        )
        tmpdb_dbh = tmpdb_client[tmpdb_name]

        #drop all existing collections
        write_progress_msg("\n ... dropping old collection", "a")
        write_progress_msg(" ... dropping tmpdb.%s" % (coll), "a")
        tmpdb_dbh[coll].drop()
        if coll in indexed_colls:
            tmpdb_dbh[coll].drop_indexes()


        for d in dir_list:
            if d[-2:] != "db":
                continue

            file_list = glob.glob(jsondb_dir + "/" + d + "/*.json")
            nrecords = 0
            for in_file in file_list:
                doc = json.loads(open(in_file, "r").read())
                if "_id" in doc:
                    doc.pop("_id")
                result = tmpdb_dbh[coll].insert_one(doc)     
                nrecords += 1
                if nrecords != 0 and nrecords%1000 == 0:
                    msg = " ... loaded %s documents to tmpdb.%s" % (nrecords,coll)
                    write_progress_msg(msg, "a")

            ts = datetime.datetime.now()
            msg = " ... finished loading %s documents to tmpdb.%s" % (nrecords, coll)
            write_progress_msg(msg, "a")

            #CREATING COLLECTION
            if coll in indexed_colls:
                msg = "\n ... creating index for tmpdb.%s" % (coll)
                write_progress_msg(msg, "a")
                res = tmpdb_dbh[coll].create_index([("$**", pymongo.TEXT)])
                msg = " ... finished creating index for tmpdb.%s" % (coll)
                write_progress_msg(msg, "a")

        # NOW CREARING DUMP DIR
        write_progress_msg("\n ... removing old tmpdb dump", "a")
        cmd = "docker exec running_glygen_mongo_%s rm -rf %s/tmpdb " % (server,dump_dir)
        x = subprocess.getoutput(cmd)


        write_progress_msg("\n ... creating new tmpdb.%s dump" % (coll), "a")
        cmd = "docker exec running_glygen_mongo_%s mongodump --username %s --password %s "
        cmd += "--db tmpdb --collection %s --out %s "
        cmd = cmd % (server, tmpdb_user, tmpdb_pass, coll, dump_dir)
        x = subprocess.getoutput(cmd)

        write_progress_msg("\n ... restoring tmpdb dump to %s.%s" % (glydb_name, coll), "a")
        cmd = "docker exec running_glygen_mongo_%s "
        cmd += "mongorestore --username %s --password %s --db %s "
        cmd += "%s/tmpdb --drop "
        cmd = cmd % (server, glydb_user, glydb_pass, glydb_name, dump_dir)
        x = subprocess.getoutput(cmd)
        write_progress_msg(" ... finished", "a")




    except pymongo.errors.ServerSelectionTimeoutError as err:
        print (err)
    except pymongo.errors.OperationFailure as err:
        print (err)



if __name__ == '__main__':
    main()
