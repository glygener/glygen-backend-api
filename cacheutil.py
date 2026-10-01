import os,sys
import string
import pytz
import datetime
from optparse import OptionParser
import glob
import json
import hashlib
import pymongo
from pymongo import MongoClient
from itertools import combinations

from copied_util import get_hash_id, make_list_objects_indirect, cache_list_objects, get_query_filter_code, get_filter_conf, get_list_objects, get_grp_id_list, get_taxid2name



def get_range_list(n):
    batch_size = int(n/10) if n > 10 else n
    range_list = []
    for i in range(0, 12):
        s = i*batch_size + 1
        e = s + batch_size
        ss = s if i == 0 else s + 1
        if e >= n:
            e = n
            range_list.append({"s":ss, "e":e})
            break
        range_list.append({"s":ss, "e":e})
    return range_list



def get_cmb_list(dbh, config_obj):

    cmb_list = []
    query_doc = get_c_initlistcache_queries(dbh, config_obj)
    for record_type in query_doc:
        for cache_name in query_doc[record_type]:
            cache_id_dict = get_cache_id_dict(dbh, cache_name)
            # for this cachename, make list cache only for site objects
            if cache_name.find("supersearch_startaa_") != -1 or cache_name.find("_flag") != -1:
                k_list = list(cache_id_dict.keys())
                for k in k_list:
                    if cache_id_dict[k] != "site":
                        cache_id_dict.pop(k)
            if cache_id_dict == {}:
                print ("no cache_id(s) related to cache_name=%s" % (cache_name))
                exit()
            for cache_id in cache_id_dict:
                cmb_list.append("%s|%s" % (cache_name, cache_id))
    return sorted(cmb_list)


def cache_exists(dbh, list_id, coll):
    doc = dbh[coll].find_one({"list_id":list_id})

    return doc != None

def delete_cache(dbh, list_id, coll):
    res = dbh[coll].delete_many({"list_id":list_id})
    return 

def get_comb_list(my_list):
    comb_list = []
    for r in range(1, len(my_list) + 1):
        combinations_at_length_r = list(combinations(my_list, r))
        comb_list.extend(combinations_at_length_r)
    return comb_list


def get_c_initcache_queries(dbh, config_obj, pulldown_dict):
    aaone2three, aathree2one = get_aa_dict()
    main_field_dict = {
        "protein":"uniprot_canonical_ac",
        "glycan":"glytoucan_ac",
        "biomarker":"biomarker_id",
        "disease":"record_id" 
    }    
    query_doc = {"protein":{},"glycan":{}, "biomarker":{}, "disease":{}}
    for record_type in query_doc:
        cache_name = record_type + "_all"
        query = {}
        query_doc[record_type][cache_name] = {"query":query,"mongoquery":{}}
        if record_type in main_field_dict:
            query_doc[record_type][cache_name]["mainfield"] = main_field_dict[record_type]
        if record_type in ["protein", "glycan"]:
            query = {"operation":"AND","query_type":"search_"+record_type}
            query_doc[record_type][cache_name]["query"] = query
            for tax_id in pulldown_dict[record_type + "_taxid2name"]:
                tax_name = pulldown_dict[record_type + "_taxid2name"][tax_id]
                cache_name = record_type + "_" + tax_name.replace(" ","_").replace("-", "_").lower()
                org_obj = {
                    "organism_list":[{"glygen_name":tax_name}], "annotation_category":"","operation":"or"
                }
                if record_type == "protein":
                    org_obj = {"id":int(tax_id), "name":tax_name}
                query = {"operation":"AND","query_type":"search_"+record_type,"organism":org_obj}
                mongoquery = {"species.taxid": {"$eq":int(tax_id)}}
                query_doc[record_type][cache_name] = {
                    "mainfield":main_field_dict[record_type], "query":query, "mongoquery":mongoquery
                }
        if record_type in ["glycan"]:
            for glycan_type in pulldown_dict["glycantype"]:
                cache_name = record_type
                cache_name += "_glycantype_" + glycan_type.replace(" ","_").replace("-", "_").lower()
                query = {"operation":"AND","query_type":"search_"+record_type,"glycan_type":glycan_type}
                mongoquery = {"classification.type.name": {"$eq": glycan_type}}
                query_doc[record_type][cache_name] = {
                    "mainfield":main_field_dict[record_type], "query":query, "mongoquery":mongoquery
                }
            for ns in pulldown_dict["glycan_namespace"]:
                cache_name = "glycan_namespace_" + ns.replace(" ","_").replace("-", "_").lower()
                cache_name = cache_name.replace(".","_")
                query = {"operation":"AND","query_type":"search_"+record_type,"id_namespace":ns}
                mongoquery = {"crossref.database" : {'$eq': ns}}
                query_doc[record_type][cache_name] = {
                    "mainfield":main_field_dict[record_type], "query":query, "mongoquery":mongoquery
                }

        if record_type in ["protein"]:
            for glyco_type in pulldown_dict["glycotype"]:
                cache_name = "protein_glycotype_" + glyco_type.replace(" ","_").replace("-", "_").lower()
                query = {"operation":"AND","query_type":"search_protein","glycosylation_type":glyco_type}
                mongoquery = {"glycosylation.type" : {"$regex": glyco_type, "$options": "i"}}
                query_doc[record_type][cache_name] = {
                    "mainfield":main_field_dict[record_type], "query":query, "mongoquery":mongoquery
                }    
            for glyco_aa in pulldown_dict["glycoaa"]:
                glyco_aa_three = aaone2three[glyco_aa] 
                cache_name = "protein_glycoaa_" + glyco_aa.replace(" ","_").replace("-", "_").lower()
                glyco_aa_obj = {"aa_list":[glyco_aa],"operation":"or"}
                query = {"operation":"AND","query_type":"search_protein","glycosylated_aa":glyco_aa_obj}
                mongoquery = {"$or":[{"glycosylation.residue" : {"$eq": glyco_aa_three}}]}
                query_doc[record_type][cache_name] = {
                    "mainfield":main_field_dict[record_type], "query":query, "mongoquery":mongoquery
                }
            for e in pulldown_dict["glycoevdn"]:
                mongoquery = pulldown_dict["glycoevdn"][e]
                
                e_type, tax_id = e, "0"
                if e.find("|") != -1:
                    e_type, tax_id = e.split("|")
                cache_name = "protein_glycoevdn_" + e_type
                tax_id = int(tax_id)
                 
                ee = e_type if tax_id == 0 else "_".join(e_type.split("_")[:-1])
                query ={"operation":"AND","query_type":"search_protein","glycosylation_evidence":ee,"tax_id":tax_id}
                query_doc[record_type][cache_name] = {
                    "mainfield":main_field_dict[record_type], "query":query, "mongoquery":mongoquery
                } 
            
    return query_doc



    
def get_supersearch_init_query(dbh, config_obj, pulldown_dict):

    doc = {"supersearch":{}}
    doc["supersearch"]["supersearch_all"] = {"query":{"empty_search_flag":True, "concept_query_list": []}}
    for record_type in ["glycan","motif","protein","site","gene","enzyme","species","disease"]:
        doc["supersearch"]["supersearch_all"]["query"]["concept_query_list"].append({"query": {}, "concept": record_type})
   
    for start_aa in pulldown_dict["supersearch_startaa"]:
        cache_name = "supersearch_startaa_" + start_aa.lower()
        doc["supersearch"][cache_name] = {
            "query":{
                "concept_query_list":[
                    {
                        "concept":"site",
                        "query":{
                            "aggregator":"$and","unaggregated_list":[
                                {"path":"site_seq","order":0,"operator":"$eq","string_value":start_aa.upper()}
                            ],
                            "aggregated_list":[]
                        }
                    } 
                ]
            }
        }
    for path in ["glycosylation_flag", "glycation_flag", "phosphorylation_flag", "mutagenesis_flag","snv_flag"]:
        cache_name = "supersearch_" + path.lower()
        doc["supersearch"][cache_name] = {
            "query":{
                "concept_query_list":[
                    {
                        "concept":"site",
                        "query":{
                            "aggregator":"$and","unaggregated_list":[
                                {"path":path,"order":0,"operator":"$eq","string_value":"true"}
                            ],
                            "aggregated_list":[]
                        }
                    }
                ]
            }
        }

    return doc


def get_supersearch_log_lines(res_obj, cache_name):

    line_list = []
    for r_type in res_obj["results_summary"]:
        obj = res_obj["results_summary"][r_type]
        list_id, result_count = obj["list_id"], obj["result_count"]
        if list_id != "":
            line_list.append("%s,%s,%s,%s" % (list_id, result_count,cache_name, r_type))
        if "bylinkage" in obj:
            for rt in obj["bylinkage"]:
                o = obj["bylinkage"][rt]
                list_id, result_count = o["list_id"], o["result_count"]
                if list_id != "":
                    line_list.append("%s,%s,%s,%s->%s" % (list_id,result_count,cache_name,r_type,rt))
        
    return line_list



def get_cache_id_dict(dbh, cache_name):
    cache_id_dict = {}
    q_obj = {"cache_info.cache_name":cache_name}
    p_obj = {"list_id":1, "cache_info.cache_name":1, "cache_info.record_type":1}
    for doc in dbh["c_initcache"].find(q_obj, p_obj):
        cache_id_dict[doc["list_id"]] = doc["cache_info"]["record_type"]
    return cache_id_dict


def get_pulldown_dict(dbh, config_obj):
    
    mq_dict = {
        "all_sites":{"glycosylation": {'$gt': []}},
        "sites_reported_with_glycans":{"glycosylation.site_category_dict.reported_with_glycan":{"$eq":True}},
        "sites_reported_without_glycans":{"glycosylation.site_category_dict.reported":{"$eq":True}},
        "all_reported_sites_with_without_glycans":{
            "$or":[
                {"glycosylation.site_category_dict.reported_with_glycan":{"$eq":True}},
                {"glycosylation.site_category_dict.reported":{"$eq":True}}
            ]
        },
        "sites_detected_by_literature_mining":{"glycosylation.site_category_dict.automatic_literature_mining":{"$eq":True}},
        "predicted_sites":{"$or":[{"glycosylation.site_category_dict.predicted":{"$eq":True}},
                {"glycosylation.site_category_dict.predicted_with_glycan":{"$eq":True}}]}
    }

    k_list = list(mq_dict.keys())
    taxid2name = get_taxid2name(dbh, default=False)
    for tax_id in taxid2name:
        tax_name = taxid2name[tax_id].lower().replace(" ","_")
        for k in k_list:
            new_k = k + "_" + tax_name + "|" + tax_id
            q = {"$and":[mq_dict[k], {"species.taxid": {'$eq': int(tax_id)}}]}
            mq_dict[new_k] = q
        


    aaone2three, aathree2one = get_aa_dict()
    tmp_dict = {}
    ts_format = "%Y-%m-%d %H:%M:%S %Z%z"
    

    #print ("flag-1", datetime.datetime.now(pytz.timezone('US/Eastern')).strftime(ts_format))
    field_one, field_two = "protein_taxid2name", "glycotype"
    field_three, field_four = "glycoevdn", "glycoaa"

    #field_five, field_six = "glycoprotein_reported", "glycoprotein_predicted"


    
    tmp_dict[field_one], tmp_dict[field_three] = {}, {}
    tmp_dict[field_two], tmp_dict[field_four] = [], []
    count_dict = {
        field_one:{}, 
        field_two:{}, 
        field_three:{},
        field_four:{}
    }

    prj_obj = {
        "species": 1, "glycosylation.type":1, "glycosylation.residue":1, "glycosylation.site_category_dict":1
    }
    idx = 0
    tmp_seen = {}
    for doc in dbh["c_protein"].find({}, prj_obj):
        idx += 1
        doc_id = str(doc["_id"])
        tax_id = doc["species"][0]["taxid"]
        tax_name = taxid2name[str(tax_id)].lower().replace(" ","_")

        if tax_id not in count_dict[field_one]:
            count_dict[field_one][tax_id] = {}
        count_dict[field_one][tax_id][doc_id] = True
       
            
        for obj in doc["glycosylation"]:
            if "type" in obj:
                val = obj["type"]
                if val != "":
                    if val not in count_dict[field_two]:
                        count_dict[field_two][val] = {}
                    count_dict[field_two][val][doc_id] = True
            val_list = ["all_sites"]
            if "site_category_dict" in obj:
                o = obj["site_category_dict"]
                for k in o:
                    if o[k] == True and k == "reported_with_glycan":
                        val_list.append("sites_reported_with_glycans")
                        val_list.append("all_reported_sites_with_without_glycans")
                    if o[k] == True and k == "reported":
                        val_list.append("sites_reported_without_glycans")
                        val_list.append("all_reported_sites_with_without_glycans")
                    if o[k] == True and k == "automatic_literature_mining":
                        val_list.append("sites_detected_by_literature_mining")
                    if o[k] == True and k == "predicted":
                        val_list.append("predicted_sites")
            for val in val_list:
                if val not in count_dict[field_three]:
                    count_dict[field_three][val] = {}
                count_dict[field_three][val][doc_id] = True
                cmb = "%s_%s|%s" % (val, tax_name,tax_id)
                if cmb not in count_dict[field_three]:
                    count_dict[field_three][cmb] = {}
                count_dict[field_three][cmb][doc_id] = True
                #print ("Robel-1",field_three, cmb, doc_id)                
                
            if "residue" in obj:
                val = obj["residue"]
                if val == "" or val not in aathree2one:
                    continue
                val = aathree2one[val]
                if val not in count_dict[field_four]:
                    count_dict[field_four][val] = {}
                count_dict[field_four][val][doc_id] = True


    for val in count_dict[field_one]:
        if len(count_dict[field_one][val].keys()) > config_obj["min_list_size_to_cache"]:
            tmp_dict[field_one][val] = taxid2name[str(val)]
    for val in count_dict[field_two]:
        if len(count_dict[field_two][val].keys()) > config_obj["min_list_size_to_cache"]:
            tmp_dict[field_two].append(val)
    for val in count_dict[field_three]:
        n = len(count_dict[field_three][val].keys())
        #print ("Robel-2",field_three, val, n, n > config_obj["min_list_size_to_cache"])
        if n > config_obj["min_list_size_to_cache"]:
            tmp_dict[field_three][val] = mq_dict[val]
    for val in count_dict[field_four]:
        if len(count_dict[field_four][val].keys()) > config_obj["min_list_size_to_cache"]:
            tmp_dict[field_four].append(val)
    




    #print ("flag-2", datetime.datetime.now(pytz.timezone('US/Eastern')).strftime(ts_format))
    field = "glycan_taxid2name"
    tmp_dict[field] = {}
    count_dict = {}
    for doc in dbh["c_glycan"].find({},{"species.taxid":1}):
        doc_id = str(doc["_id"])
        for obj in doc["species"]:
            val = obj["taxid"]
            if val not in count_dict:
                count_dict[val] = {}
            count_dict[val][doc_id] = True
    for val in count_dict:
        if len(count_dict[val].keys()) > config_obj["min_list_size_to_cache"]:
            tmp_dict[field][val] = taxid2name[str(val)]
  
   
    #print ("flag-3", datetime.datetime.now(pytz.timezone('US/Eastern')).strftime(ts_format))
    
    field = "glycantype"
    tmp_dict[field] = []
    count_dict = {}
    for doc in dbh["c_glycan"].find({},{"classification.type.name":1}):
        doc_id = str(doc["_id"])
        for obj in doc["classification"]:
            if "type" not in obj:
                continue
            if "name" not in obj["type"]:
                continue
            val = obj["type"]["name"]
            if val == "":
                continue
            if val not in count_dict:
                count_dict[val] = {}
            count_dict[val][doc_id] = True
    for val in count_dict:
        if len(count_dict[val].keys()) > config_obj["min_list_size_to_cache"]:
            tmp_dict[field].append(val) 

    #print ("flag-4", datetime.datetime.now(pytz.timezone('US/Eastern')).strftime(ts_format))
    field = "glycan_namespace"
    tmp_dict[field] = []
    count_dict = {}
    for doc in dbh["c_glycan"].find({},{"crossref.database":1}):
        doc_id = str(doc["_id"])
        for obj in doc["crossref"]:
            val = obj["database"]
            if val not in count_dict:
                count_dict[val] = {}
            count_dict[val][doc_id] = True
    for val in count_dict:
        if len(count_dict[val].keys()) > config_obj["min_list_size_to_cache"]:
            tmp_dict[field].append(val)


    #print ("flag-5", datetime.datetime.now(pytz.timezone('US/Eastern')).strftime(ts_format))

    field = "supersearch_startaa"
    tmp_dict[field] = []
    count_dict = {}
    idx = 0
    for doc in dbh["c_site"].find({},{"start_aa":1}):
        idx += 1
        if "start_aa" in doc:
            val = doc["start_aa"]
            if val != "":
                if val not in count_dict:
                    count_dict[val] = 0
                count_dict[val] += 1
    for val in count_dict:
        if count_dict[val] > config_obj["min_list_size_to_cache"]:
            tmp_dict[field].append(val)

    

    return tmp_dict

def get_column_dict():
    
    tmp_dict = {
        "protein":["uniprot_canonical_ac","gene_name","protein_name","hit_score",
            "organism","length","mass","refseq_name","refseq_ac","uniprot_id"],
        "glycan":["glytoucan_ac","image_url","hit_score","mass","byonic","publication"],
        "biomarker":[],
        "disease":[],
        "supersearch":["uniprot_canonical_ac","protein_name","organism","hit_score",
            "start_pos","end_pos","gene_name"]
    }
    
    return tmp_dict


def get_c_initlistcache_queries(dbh, config_obj):
    aaone2three, aathree2one = get_aa_dict()
    column_dict = get_column_dict()
    query_doc = {"protein":{},"glycan":{}, "biomarker":{}, "disease":{}, "supersearch":{}} 
    seen_cache_name = {}
    for doc in dbh["c_initcache"].find({}, {"list_id":1,"cache_info":1, "total_count":1}):
        if "cache_info" not in doc:
            continue
        cache_info = doc["cache_info"]
        if "cache_name" not in cache_info:
            continue
        cache_name = cache_info["cache_name"]
        record_type = cache_info["record_type"]
        cmb = "%s|%s" % (cache_name, record_type)
        seen_cache_name[cmb] = True

    for cmb in seen_cache_name:
        cache_name, record_type = cmb.split("|")
        record_type = "supersearch" if record_type == "site" else record_type   
        #record_type = cache_name.split("_")[0]
        query = {"id":"", "offset":1,"limit":20,"order":"desc","sort":"hit_score","filters":[]}
        query["columns"] = []
        if record_type in column_dict:
            query["columns"] = column_dict[record_type]
        query_doc[record_type][cache_name] = {"query":query} 
        #print (cache_name, record_type, query["columns"])


    return query_doc



def get_aa_dict():
    tmp_dict_one = {
        "A":"Ala","R":"Arg","N":"Asn","D":"Asp","C":"Cys","E":"Glu","Q":"Gln",
        "G":"Gly","H":"His","I":"Ile","L":"Leu","K":"Lys","M":"Met","F":"Phe",
        "P":"Pro","S":"Ser","T":"Thr","W":"Trp","Y":"Tyr","V":"Val",
    }
    tmp_dict_two = {}
    for aaone in tmp_dict_one:
        tmp_dict_two[tmp_dict_one[aaone]] = aaone
    return tmp_dict_one, tmp_dict_two
