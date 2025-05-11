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
    parser.add_option("-c","--coll",action="store",dest="coll",help="OPTIONAL c_glycan,c_protein ")
    parser.add_option("-v","--dataversion",action="store",dest="dataversion",help="2.0.2/2.0.3 ...")
 
    (options,args) = parser.parse_args()
    for key in ([options.server, options.dataversion, options.coll]):
        if not (key):
            parser.print_help()
            sys.exit(0)

    global log_file

    server = options.server
    coll = options.coll
    rel = options.dataversion


    main_id_dict = {
        "c_protein":"uniprot_canonical_ac",
        "c_glycan":"glytoucan_ac",
        "c_site":"id"
    }

    if coll not in main_id_dict:
        print ("coll is not in main_id_dict")
        exit()
    main_id = main_id_dict[coll]

    rel_dir = "/data/shared/glygen/releases/data/v-%s/" % (rel)
    record_id_list = []
    file_list = glob.glob(rel_dir + "jsondb/patchdb/*.json")
    for in_file in file_list:
        record_id = in_file.split("/")[-1].replace(".json", "")
        record_id_list.append(record_id)


    db_name = "glydb_beta" if server == "beta" else "glydb"
    config_obj = json.loads(open("./conf/config.json", "r").read())
    mongo_port = "27017"
    host = "mongodb://127.0.0.1:%s" % (mongo_port)
  
    db_obj = config_obj["dbinfo"][db_name]
    glydb_name, db_user, db_pass =  db_obj["db"], db_obj["user"], db_obj["password"]
    
    log_file = "logs/%s_patch_progress_%s.txt" % (coll, server)
    msg = "\n ... started loading to %s.%s" % (glydb_name, coll)
    write_progress_msg(msg, "w")


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

        batch_size = 100
        total = len(record_id_list)
        nparts = int(total/batch_size) + 1 
        for idx in range(0, nparts):
            start = idx*batch_size  
            end = start + batch_size
            if end > total:
                end = total
            if end > start:
                q = {main_id:{"$in": record_id_list[start:end]}}
                res = dbh[coll].delete_many(q)
                msg = " ... deleted (start=%s end=%s) records from %s.%s" % (start, end, glydb_name, coll)
                write_progress_msg(msg, "a")    


        idx = 1
        for record_id in record_id_list:
            in_file = rel_dir + "jsondb/patchdb/%s.json" % (record_id)
            doc = json.load(open(in_file))
            res = dbh[coll].insert_one(doc)     
            if idx%100 == 0:
                msg = " ... loaded (%s/%s) records into %s.%s" % (idx, total, glydb_name, coll)
                write_progress_msg(msg, "a")
            idx += 1

    except pymongo.errors.ServerSelectionTimeoutError as err:
        print (err)
    except pymongo.errors.OperationFailure as err:
        print (err)



if __name__ == '__main__':
    main()
