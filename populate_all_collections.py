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
    with open("logs/data_loading_progress.txt", flag) as F:
        if msg.strip() == "":
            F.write("%s\n" % (msg))
        else:
            F.write("%s [%s]\n" % (msg, ts))
    return

            

###############################
def main():


    usage = "\n%prog  [options]"
    parser = OptionParser(usage,version="%prog version___")
    parser.add_option("-s","--server",action="store",dest="server",help="dev/tst/beta/prd")
    parser.add_option("-v","--dataversion",action="store",dest="dataversion",help="2.0.2/2.0.3 ...")
        
    (options,args) = parser.parse_args()

    for key in ([options.server, options.dataversion]):
        if not (key):
            parser.print_help()
            sys.exit(0)

    server = options.server
    ver = options.dataversion
    mode = "full"


    config_obj = json.loads(open("./conf/config.json", "r").read())
    mongo_port = config_obj["dbinfo"]["port"][server]
    host = "mongodb://127.0.0.1:%s" % (mongo_port)

    jsondb_dir = config_obj["data_path"] + "/releases/data/v-%s/jsondb/" % (ver)
    dump_dir = config_obj["data_path"] + "/mongodump/"

    dir_list = config_obj["downloads"]["jsondb"]
    #dir_list = os.listdir(jsondb_dir)
    
    tmpdb_user = config_obj["dbinfo"]["tmpdb"]["user"]
    tmpdb_pass = config_obj["dbinfo"]["tmpdb"]["password"]
    tmpdb_name =  config_obj["dbinfo"]["tmpdb"]["db"] 
    
    db_user = config_obj["dbinfo"]["glydb"]["user"]
    db_pass = config_obj["dbinfo"]["glydb"]["password"]
    db_name =  config_obj["dbinfo"]["glydb"]["db"]
    indexed_colls = ["c_protein", "c_glycan"]


    msg = "\n ... started loading data version %s" % (ver)
    write_progress_msg(msg, "w")


    try:
        client = pymongo.MongoClient(host,
            username=tmpdb_user,
            password=tmpdb_pass,
            authSource=tmpdb_name,
            authMechanism='SCRAM-SHA-1',
            serverSelectionTimeoutMS=10000
        )
        client.server_info()
        dbh = client[tmpdb_name]
       
        #drop all existing collections
        write_progress_msg("\n ... dropping old collections", "a")
        for c in dbh.list_collection_names():
            write_progress_msg(" ... dropping tmpdb.%s" % (c), "a")
            dbh[c].drop()
            dbh[c].drop_indexes()

        dir_list.remove("proteindb")
        dir_list.remove("glycandb")
        dir_list = ["glycandb", "proteindb"] + dir_list

        coll_list = []
        for d in dir_list:
            if d[-2:] != "db":
                continue
            coll = "c_" + d[:-2]
            if coll == "c_jumbo":
                continue
            coll_list.append(coll)
            write_progress_msg("\n ... clearing tmpdb.%s" % (coll), "a")        
            result = dbh[coll].delete_many({})

            file_list = glob.glob(jsondb_dir + "/" + d + "/*.json")
            if mode == "partial":
                file_list = file_list[:1000]
            nrecords = 0
            for in_file in file_list:
                doc = json.loads(open(in_file, "r").read())
                if "_id" in doc:
                    doc.pop("_id")
                result = dbh[coll].insert_one(doc)     
                nrecords += 1
                if nrecords != 0 and nrecords%1000 == 0:
                    msg = " ... loaded %s documents to tmpdb.%s" % (nrecords,coll)
                    write_progress_msg(msg, "a")

            ts = datetime.datetime.now()
            msg = " ... finished loading %s documents to tmpdb.%s" % (nrecords, coll)
            write_progress_msg(msg, "a")

            #CREATING COLLECTION
            if coll in indexed_colls:
                msg = " ... creating index for tmpdb.%s" % (coll)
                write_progress_msg(msg, "a")
                res = dbh[coll].create_index([("$**", pymongo.TEXT)])
                msg = " ... finished creating index for tmpdb.%s" % (coll)
                write_progress_msg(msg, "a")

        # NOW CLEARING DUMP DIR
        write_progress_msg(" ... removing old tmpdb dump", "a")
        cmd = "docker exec running_glygen_mongo_%s rm -rf %s/tmpdb " % (server, dump_dir)
        x = subprocess.getoutput(cmd)

        write_progress_msg(" ... creating new tmpdb dump", "a")
        cmd = "docker exec running_glygen_mongo_%s mongodump --username %s --password %s "
        cmd += "--db tmpdb --out %s"
        cmd = cmd % (server, tmpdb_user, tmpdb_pass, dump_dir)
        x = subprocess.getoutput(cmd)

        write_progress_msg(" ... restoring tmpdb dump to %s" % (db_name), "a")
        cmd = "docker exec running_glygen_mongo_%s "
        cmd += "mongorestore --username %s --password %s --db %s "
        cmd += "%s/tmpdb --drop"
        cmd = cmd % (server, db_user, db_pass, db_name, dump_dir)
        x = subprocess.getoutput(cmd)

        write_progress_msg("", "a")
        for coll in coll_list:
            n = dbh[coll].count_documents({})
            write_progress_msg(" ... loaded %s documents to %s" % (n, coll), "a")
       
        write_progress_msg("", "a")




    except pymongo.errors.ServerSelectionTimeoutError as err:
        print (err)
    except pymongo.errors.OperationFailure as err:
        print (err)



if __name__ == '__main__':
    main()
