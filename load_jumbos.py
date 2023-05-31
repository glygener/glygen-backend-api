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
    parser.add_option("-c","--coll",action="store",dest="coll",help="OPTIONAL c_glycan,c_protein ")

    (options,args) = parser.parse_args()

    for key in ([options.server, options.dataversion, options.coll]):
        if not (key):
            parser.print_help()
            sys.exit(0)

    global log_file

    server = options.server
    ver = options.dataversion
    coll = options.coll

    config_obj = json.loads(open("./conf/config.json", "r").read())
    mongo_port = config_obj["dbinfo"]["port"][server]
    host = "mongodb://127.0.0.1:%s" % (mongo_port)
    jsondb_dir = config_obj["data_path"] + "/releases/data/v-%s/jsondb/" % (ver)
    glydb_user = config_obj["dbinfo"]["glydb"]["user"]
    glydb_pass = config_obj["dbinfo"]["glydb"]["password"]
    glydb_name =  config_obj["dbinfo"]["glydb"]["db"]

    coll_list = ["c_protein", "c_glycan", "c_list", "c_publication"]
    list_dict = {}
    main_id_field = {"c_protein":"uniprot_canonical_ac", "c_glycan":"glytoucan_ac", "c_publication":"record_id"}
    for c in coll_list:
        list_dict[c] = []

    try:
        glydb_client = pymongo.MongoClient(host,
            username=glydb_user,
            password=glydb_pass,
            authSource=glydb_name,
            authMechanism='SCRAM-SHA-1',
            serverSelectionTimeoutMS=10000
        )
        dbh = glydb_client[glydb_name]

        tmp_list = glob.glob(jsondb_dir + "/jumbodb/*.json")
        for in_file in tmp_list:
            file_name = in_file.split("/")[-1]
            if file_name.find("pubmed") != -1:
                list_dict["c_publication"].append(in_file)
            elif file_name.find("G49108TO") != -1:
                list_dict["c_glycan"].append(in_file)
                list_dict["c_list"].append(in_file)
            else:
                list_dict["c_protein"].append(in_file)
                list_dict["c_list"].append(in_file)

        nrecords = 0
        file_list = list_dict[coll]
        for f in file_list:
            file_name = f.split("/")[-1]
            json_db = coll[2:] + "db"
            in_file = jsondb_dir + "/" + json_db + "/" + file_name
            if os.path.isfile(in_file) == False:
                print ("file doesn't exist: %s" % (in_file))
                exit(-1)
            doc = json.loads(open(in_file, "r").read())
        
            main_field = main_id_field[coll] if coll in main_id_field else ""
            if coll == "c_list":
                main_field = main_id_field["c_protein"] 
                main_field = main_id_field["c_glycan"] if file_name.find("G49108TO") != -1 else main_field

            main_id = file_name.replace(".json", "")
            q = {main_field:main_id}
            res = dbh[coll].delete_one(q)
            print ("Removed %s from %s" % (main_id, coll))
            res = dbh[coll].insert_one(doc)     
            print ("Inserted %s from %s" % (main_id, coll))
            

    except pymongo.errors.ServerSelectionTimeoutError as err:
        print (err)
    except pymongo.errors.OperationFailure as err:
        print (err)



if __name__ == '__main__':
    main()
