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

__version__="1.0"
__status__ = "Dev"


def xxxx(dbh, search_field_dict, field2sec, api_name):

    record_type = api_name.split("_")[0]
    hit_dict, hit_stat = {}, {}
    for f in search_field_dict:
        query_obj_single = {f:search_field_dict[f], "operation":"AND", "query_type":"search_protein"}
        list_id_single = get_hash_id(api_name, record_type, query_obj_single)
        cached_obj_single = dbh["c_initcache"].find_one({"list_id":list_id_single})
        if cached_obj_single != None:
            hit_dict[f] = []
            for doc in dbh["c_initcache"].find({"list_id":list_id_single}):
                hit_dict[f] += doc["results"]
            hit_stat[f] = {"n":len(hit_dict[f]), "flag":"1"}
        elif f in field2sec:
            hit_dict[f] = []
            sec = field2sec[f]
            f_parts = f.split(".")
            val = search_field_dict[f]
            if type(val) is dict:
                for ff in f_parts[1:]:
                    val = val[ff]
            query_obj_new = {"term":val,"term_category":sec}
            api_name_simple = "%s_search_simple" % (record_type)
            res = use_indexed_search(api_name_simple, query_obj_new,config_obj)
            if "error_list" not in res:
                for doc in dbh["c_usercache"].find({"list_id":res["list_id"]}):
                    hit_dict[f] += doc["results"]
            hit_stat[f] = {"n":len(hit_dict[f]), "flag":"2"}
        elif f == "glycosylated_aa":
            aa_list = search_field_dict[f]["aa_list"]
            op = search_field_dict[f]["operation"]
            hit_dict[f] = run_special_query(dbh, collection,api_name, record_type, aa_list, op)
            hit_stat[f] = {"n":len(hit_dict[f]), "flag":"3"}
        elif f == "uniprot_canonical_ac":
            hit_dict[f] = []
            mongo_query_single = get_mongo_query(query_obj_single, glygen_name_dict)
            prj_obj = {"uniprot_canonical_ac":1, "uniprot_ac":1, "uniprot_id":1, "isoforms.isoform_ac":1}
            for obj in dbh[collection].find(mongo_query_single,prj_obj):
                canon = obj["uniprot_canonical_ac"]
                hit_dict[f].append(canon)
                uniprot_ac, uniprot_id = obj["uniprot_ac"], obj["uniprot_id"]
                seen_id[canon] = True
                seen_id[uniprot_ac] = True
                seen_id[uniprot_id] = True
                for o in obj["isoforms"]:
                    seen_id[o["isoform_ac"]] = True
            hit_stat[f] = {"n":len(hit_dict[f]), "flag":"4", "mquery":mongo_query_single}
        else:
            hit_dict[f] = []
            mongo_query_single = get_mongo_query(query_obj_single, glygen_name_dict)
            prj_obj = {"uniprot_canonical_ac":1}
            for obj in dbh[collection].find(mongo_query_single,prj_obj):
                canon = obj["uniprot_canonical_ac"]
                hit_dict[f].append(canon)
            hit_stat[f] = {"n":len(hit_dict[f]), "flag":"5", "mquery":mongo_query_single}
        ts_list.append("1y-"+datetime.datetime.now(pytz.timezone('US/Eastern')).strftime(ts_format))

    return hit_dict, hit_stat, seen_id





###############################
def main():


    server = "tst"
    coll = "c_protein"
    aa_map = {
        "A":"Ala","R":"Arg","N":"Asn","D":"Asp","C":"Cys","E":"Glu","Q":"Gln",
        "G":"Gly","H":"His","I":"Ile","L":"Leu","K":"Lys","M":"Met","F":"Phe",
        "P":"Pro","S":"Ser","T":"Thr","W":"Trp","Y":"Tyr","V":"Val"
    }

    db_name = "glydb_beta" if server == "beta" else "glydb"

    config_obj = json.loads(open("./conf/config.json", "r").read())
    #mongo_port = config_obj["dbinfo"]["port"][server]
    mongo_port = "27017"
    host = "mongodb://127.0.0.1:%s" % (mongo_port)
  
    db_obj = config_obj["dbinfo"][db_name]
    glydb_name, db_user, db_pass =  db_obj["db"], db_obj["user"], db_obj["password"]

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

        ts_format = "%Y-%m-%d %H:%M:%S %Z%z"
        ts_list = []
        ts_list.append("1- "+datetime.datetime.now(pytz.timezone('US/Eastern')).strftime(ts_format))
       
        hit_dict_local = {} 
        aa_list = ["N", "T", "X"]
        op = "or"
        for aa in aa_list:
            ts_list.append(aa)
            ts_list.append("a- "+datetime.datetime.now(pytz.timezone('US/Eastern')).strftime(ts_format))
            aa_three = aa_map[aa] if aa in aa_map else aa
            qry_obj = {"glycosylation.residue":{"$eq":aa_three}}
            prj_obj = {"uniprot_canonical_ac":1}
            tmp_dict = {}
            for obj in dbh[coll].find(qry_obj,prj_obj):
                canon = obj["uniprot_canonical_ac"]
                tmp_dict[canon] = True
            hit_dict_local[aa] = list(tmp_dict.keys())
            ts_list.append("b- "+datetime.datetime.now(pytz.timezone('US/Eastern')).strftime(ts_format))
            
        record_list = []
        if op == "and":
            record_list = hit_dict_local[aa_list[0]]
            if len(aa_list) > 1:
                for aa in aa_list[1:]:
                    ts_list.append("x- "+datetime.datetime.now(pytz.timezone('US/Eastern')).strftime(ts_format))
                    record_list = list(set(record_list).intersection(set(hit_dict_local[aa])))
                    ts_list.append("y- "+datetime.datetime.now(pytz.timezone('US/Eastern')).strftime(ts_format))
            
        else:
            for aa in hit_dict_local:
                ts_list.append("x- "+datetime.datetime.now(pytz.timezone('US/Eastern')).strftime(ts_format))
            
                record_list += hit_dict_local[aa]
                ts_list.append("y- "+datetime.datetime.now(pytz.timezone('US/Eastern')).strftime(ts_format))
            
            record_list = list(set(record_list))

        ts_list.append("2- "+datetime.datetime.now(pytz.timezone('US/Eastern')).strftime(ts_format))
        print (len(record_list))
        print (json.dumps(ts_list, indent=4))
    except pymongo.errors.ServerSelectionTimeoutError as err:
        print (err)
    except pymongo.errors.OperationFailure as err:
        print (err)



if __name__ == '__main__':
    main()
