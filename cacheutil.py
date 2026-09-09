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
            for e_type in pulldown_dict["glycoevdn"]:
                cache_name = "protein_glycoevdn_" + e_type
                query = {"operation":"AND","query_type":"search_protein","glycosylation_evidence":e_type}
                mongoquery = {"$or":[pulldown_dict["glycoevdn"][e_type]]}
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
        "sites_reported_with_glycans":{"glycosylation.site_category_dict.reported_with_glycan":{"$eq":True}},
        "sites_reported_without_glycans":{"glycosylation.site_category_dict.reported":{"$eq":True}},
        "sites_detected_by_literature_mining":{"glycosylation.site_category_dict.automatic_literature_mining":{"$eq":True}},
        "predicted_sites":{"$or":[{"glycosylation.site_category_dict.predicted":{"$eq":True}},
                {"glycosylation.site_category_dict.predicted_with_glycan":{"$eq":True}}]}
    }


    tmp_dict = {}

    taxid2name = get_taxid2name(dbh, default=False)
    field = "protein_taxid2name"
    tmp_dict[field] = {}
    count_dict = {}
    for doc in dbh["c_protein"].find({},{"species.taxid":1}):
        doc_id = str(doc["_id"])
        val = doc["species"][0]["taxid"]
        if val not in count_dict:
            count_dict[val] = {} 
        count_dict[val][doc_id] = True 
    for val in count_dict:
        if len(count_dict[val].keys()) > config_obj["min_list_size_to_cache"]:
            tmp_dict[field][val] = taxid2name[str(val)]

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
  
     
    field = "glycotype"
    tmp_dict[field] = []
    count_dict = {}
    for doc in dbh["c_protein"].find({},{"glycosylation.type":1}):
        doc_id = str(doc["_id"])
        for obj in doc["glycosylation"]:
            if "type" not in obj:
                continue
            val = obj["type"]
            if val == "":
                continue
            if val not in count_dict:
                count_dict[val] = {}
            count_dict[val][doc_id] = True
    for val in count_dict:
        if len(count_dict[val].keys()) > config_obj["min_list_size_to_cache"]:
            tmp_dict[field].append(val)

    field = "glycoevdn"
    tmp_dict[field] = {}
    count_dict = {}
    for doc in dbh["c_protein"].find({},{"glycosylation.site_category_dict":1}):
        doc_id = str(doc["_id"])
        for obj in doc["glycosylation"]:
            if "site_category_dict" not in obj:
                continue
            o = obj["site_category_dict"]
            val_list = []
            for k in o:
                if o[k] == True and k == "reported_with_glycan":
                    val_list.append("sites_reported_with_glycans")
                if o[k] == True and k == "reported":
                    val_list.append("sites_reported_without_glycans") 
                if o[k] == True and k == "automatic_literature_mining":
                    val_list.append("sites_detected_by_literature_mining")
                if o[k] == True and k == "predicted":
                    val_list.append("predicted_sites")
            for val in val_list:
                if val not in count_dict:
                    count_dict[val] = {}
                count_dict[val][doc_id] = True
    for val in count_dict:
        if len(count_dict[val].keys()) > config_obj["min_list_size_to_cache"]:
            tmp_dict[field][val] = mq_dict[val]
 
                
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
 

    aaone2three, aathree2one = get_aa_dict()
    field = "glycoaa"
    tmp_dict[field] = []
    count_dict = {}
    for doc in dbh["c_protein"].find({},{"glycosylation.residue":1}):
        doc_id = str(doc["_id"])
        for obj in doc["glycosylation"]:
            if "residue" not in obj:
                continue
            val = obj["residue"]
            if val == "" or val not in aathree2one:
                continue
            val = aathree2one[val]
            if val not in count_dict:
                count_dict[val] = {}
            count_dict[val][doc_id] = True
    for val in count_dict:
        if len(count_dict[val].keys()) > config_obj["min_list_size_to_cache"]:
            tmp_dict[field].append(val)

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

    
    field = "supersearch_startaa"
    tmp_dict[field] = []
    count_dict = {}
    for doc in dbh["c_site"].find({},{"start_aa":1}):
        doc_id = str(doc["_id"])
        if "start_aa" not in doc:
            continue
        val = doc["start_aa"]
        if val == "":
            continue
        if val not in count_dict:
            count_dict[val] = {}
        count_dict[val][doc_id] = True
    for val in count_dict:
        if len(count_dict[val].keys()) > config_obj["min_list_size_to_cache"]:
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
