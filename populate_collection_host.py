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



def collapse_objects(obj_list):

    seen = {}
    obj_dict = {}
    for obj in obj_list:
        canon = obj["uniprot_canonical_ac"] if "uniprot_canonical_ac" in obj else ""
        aa_pos = obj["start_pos"] if "start_pos" in obj else ""
        tissue_obj = obj["tissue"]
        cell_line_obj = obj["cell_line"]
        sample_src_id = cell_line_obj["id"] if tissue_obj == {} else tissue_obj["id"]
        combo_id_one = "%s|%s|%s" % (canon,aa_pos,sample_src_id)
        if combo_id_one not in seen:
            if "abundance" in obj:
                obj.pop("abundance")
            seen[combo_id_one] = {}
            obj_dict[combo_id_one] = obj
        for ev_obj in obj["evidence"]:
            combo_id_two = json.dumps(ev_obj)
            seen[combo_id_one][combo_id_two] = True
    
    new_obj_list = []
    for combo_id_one in seen:
        obj = obj_dict[combo_id_one]
        obj["evidence"] = []
        for combo_id_two in seen[combo_id_one]:
            obj["evidence"].append(json.loads(combo_id_two))
        new_obj_list.append(obj)
    
    return new_obj_list

def write_progress_msg(msg, flag):
    ts = datetime.datetime.now()
    with open(log_file,  flag) as F:
        F.write("%s [%s]\n" % (msg, ts))
    return

            

def get_coll_list(db_list):
    coll_list = []
    for d in db_list:
        if d[-2:] != "db":
            continue                                    
        coll = "c_" + d[:-2]
        if coll in ["c_jumbo"]:
            continue                                                                            
        coll_list.append(coll)
    
    return coll_list


def get_archived_docs(coll):

    tmp_list = []

    cmd = "ls -tr " + "/data/shared/glygen/archive/%s-*.json" % (coll)
    file_list = subprocess.getoutput(cmd).split("\n")
    in_file = file_list[-1]

    doc_list = []
    b = open(in_file, "r").read()
    if b.strip() != "":
        tmp_list = json.loads(b)
        for doc in tmp_list:
            if "_id" in doc:
                doc.pop("_id")
            for p in ["start_date", "end_date", "createdts", "updatedts"]:
                if p in doc:
                    doc[p] = datetime.datetime.strptime(doc[p].split(".")[0], '%Y-%m-%d %H:%M:%S')
            doc_list.append(doc)

    return doc_list


###############################
def main():


    usage = "\n%prog  [options]"
    parser = OptionParser(usage,version="%prog version___")
    parser.add_option("-s","--server",action="store",dest="server",help="dev/tst/beta/prd")
    parser.add_option("-v","--dataversion",action="store",dest="dataversion",help="2.0.2/2.0.3 ...")
    parser.add_option("-c","--coll",action="store",dest="coll",help="OPTIONAL c_glycan,c_protein ")
        
    (options,args) = parser.parse_args()

    for key in ([options.server, options.dataversion]):
        if not (key):
            parser.print_help()
            sys.exit(0)

    global log_file

    server = options.server
    ver = options.dataversion


    db_name = "glydb_beta" if server == "beta" else "glydb"
    
    config_obj = json.loads(open("./conf/config.json", "r").read())
    #mongo_port = config_obj["dbinfo"]["port"][server]
    mongo_port = "27017"

    host = "mongodb://127.0.0.1:%s" % (mongo_port)
    jsondb_dir = config_obj["data_path"] + "/releases/data/v-%s/jsondb/" % (ver)
    dump_dir = config_obj["data_path"] + "/mongodump/"
    tmpdb_user = config_obj["dbinfo"]["tmpdb"]["user"]
    tmpdb_pass = config_obj["dbinfo"]["tmpdb"]["password"]
    tmpdb_name =  config_obj["dbinfo"]["tmpdb"]["db"]
 
    glydb_user = config_obj["dbinfo"][db_name]["user"]
    glydb_pass = config_obj["dbinfo"][db_name]["password"]
    glydb_name =  config_obj["dbinfo"][db_name]["db"]
    #text_indexed_colls = [
    #    "c_protein", "c_glycan", "c_motif", "c_publication", "c_biomarker","c_idtrack", 
    #    "c_network", "c_disease"
    #]
    text_indexed_colls = []
    index_dict = json.load(open("conf/indexes.json"))

    archived_colls = ["c_video", "c_outreach", "c_event"]

    db_list = config_obj["downloads"]["jsondb"]
    coll_list = get_coll_list(db_list)
    if options.coll != None:
        coll_list =  options.coll.split(",")


    #coll_list.remove("c_protein")
    #coll_list.remove("c_list")
    #print (coll_list)
    #exit()


    try:
        tmpdb_client = pymongo.MongoClient(host,
            username=tmpdb_user,
            password=tmpdb_pass,
            authSource=tmpdb_name,
            authMechanism='SCRAM-SHA-1',
            serverSelectionTimeoutMS=10000
        )
        tmpdb_dbh = tmpdb_client[tmpdb_name]



        for coll in coll_list:

            log_file = "logs/%s_loading_progress_%s.txt" % (coll, server)
            msg = "\n ... started loading %s.%s version %s" % (glydb_name, coll, ver)
            write_progress_msg(msg, "w")

            #drop all existing collections 
            write_progress_msg(" ... dropping tmpdb.%s" % (coll), "a")
            tmpdb_dbh[coll].drop()

            if coll in text_indexed_colls:
                tmpdb_dbh[coll].drop_indexes()
            if coll in archived_colls:
                doc_list = get_archived_docs(coll)
                nrecords_total = len(doc_list)
                nrecords = 0
                for doc in doc_list:
                    result = tmpdb_dbh[coll].insert_one(doc)
                    nrecords += 1
                    if nrecords != 0 and nrecords%1000 == 0:
                        msg = " ... loaded %s out of %s documents to tmpdb.%s" % (nrecords, nrecords_total, coll)
                        write_progress_msg(msg, "a") 
            else:
                json_db = coll[2:] + "db"
                file_list = glob.glob(jsondb_dir + "/" + json_db + "/*.json")
                #file_list = glob.glob(jsondb_dir + "/" + json_db + "/G17689DH*.json")
                #exit()

                nrecords_total = len(file_list)
                nrecords = 0
                for in_file in file_list:
                    doc = json.loads(open(in_file, "r").read())
                    if "_id" in doc:
                        doc.pop("_id")

                    #collapse glycan expression objects in c_glycan and c_batch
                    if coll == "c_glycan":
                        if len(doc["expression"]) > 0:
                            doc["expression"] = collapse_objects(doc["expression"])
                    if coll == "c_batch":
                        if "expression" in doc["sections"]:
                            doc["sections"]["expression"] = collapse_objects(doc["sections"]["expression"])
                    if coll in ["c_index"]:
                        for obj in doc:
                            result = tmpdb_dbh[coll].insert_one(obj)
                    else:
                        result = tmpdb_dbh[coll].insert_one(doc)     
                    nrecords += 1
                    if nrecords != 0 and nrecords%1000 == 0:
                        msg = " ... loaded %s out of %s documents to tmpdb.%s" % (nrecords, nrecords_total, coll)
                        write_progress_msg(msg, "a")
                
            ts = datetime.datetime.now()
            msg = " ... finished loading %s out of %s documents to tmpdb.%s" % (nrecords,nrecords_total, coll)
            write_progress_msg(msg, "a")

            #CREATING COLLECTION
            if coll in text_indexed_colls:
                msg = "\n ... creating text index for tmpdb.%s" % (coll)
                write_progress_msg(msg, "a")
                res = tmpdb_dbh[coll].create_index([("$**", pymongo.TEXT)])
                msg = " ... finished creating text index for tmpdb.%s" % (coll)
                write_progress_msg(msg, "a")

            if coll in index_dict:
                index_name_list = []
                for cur in tmpdb_dbh[coll].list_indexes():
                    index_name_list.append(cur["name"])
                for path in index_dict[coll]:
                    index_name = index_dict[coll][path]
                    if index_name in index_name_list:
                        msg = "\n ... dropping field index (path=%s) for tmpdb.%s" % (path, coll)
                        write_progress_msg(msg, "a")
                        res = tmpdb_dbh[coll].drop_index(index_name)
                        msg = " ... finished dropping field index (path=%s) for tmpdb.%s"%(path,coll)
                        write_progress_msg(msg, "a")

                    msg = "\n ... creating field index (path=%s) for tmpdb.%s" % (path, coll)
                    write_progress_msg(msg, "a")
                    res = tmpdb_dbh[coll].create_index([(path, -1 )], name=index_name)
                    msg = " ... finished creating field index (path=%s) for tmpdb.%s" % (path, coll)
                    write_progress_msg(msg, "a")



            # NOW CREARING DUMP DIR
            write_progress_msg("\n ... removing old tmpdb dump", "a")
            cmd = "rm -rf %s/tmpdb " % (dump_dir)
            x = subprocess.getoutput(cmd)


            write_progress_msg("\n ... creating new tmpdb.%s dump" % (coll), "a")
            cmd = "mongodump --username %s --password %s "
            cmd += "--db tmpdb --collection %s --out %s "
            cmd = cmd % (tmpdb_user, tmpdb_pass, coll, dump_dir)
            x = subprocess.getoutput(cmd)

            write_progress_msg("\n ... restoring tmpdb dump to %s.%s" % (glydb_name, coll), "a")
            cmd = "mongorestore --username %s --password %s --db %s "
            cmd += "%s/tmpdb --drop "
            cmd = cmd % (glydb_user, glydb_pass, glydb_name, dump_dir)
            x = subprocess.getoutput(cmd)
            write_progress_msg("\n ... finished restoring", "a") 


            #update supersearch_init
            if coll == "c_searchinit":
                cmd = "python3 update-search-init.py -s %s" % (server)
                x = subprocess.getoutput(cmd)


    except pymongo.errors.ServerSelectionTimeoutError as err:
        print (err)
    except pymongo.errors.OperationFailure as err:
        print (err)



if __name__ == '__main__':
    main()
