import os
import string
import random
import hashlib
import json
import datetime,time
import pytz
from collections import OrderedDict
from bson import json_util, ObjectId

from glygen.indexlib import use_indexed_search
from glygen.db import get_mongodb
from glygen.util import get_errors_in_query, sort_objects, order_obj, clean_obj, get_paginated_sections, cache_hitlist, transform_query_term, get_hash_id


def disease_search_init(config_obj):

    dbh, error_obj = get_mongodb()
    if error_obj != {}:
        return error_obj

    #Collect errors 
    error_list = get_errors_in_query("disease_searchinit",{}, config_obj)
    if error_list != []:
        return {"error_list":error_list}

    collection = "c_searchinit"
    res_obj =  dbh[collection].find_one({})

    
    return res_obj["disease"] if "disease" in res_obj else {}




def search_simple(query_obj, config_obj):

    dbh, error_obj = get_mongodb()
    if error_obj != {}:
        return error_obj


    #Collect errors 
    error_list = get_errors_in_query("disease_search_simple", query_obj,config_obj)
    if error_list != []:
        return {"error_list":error_list}


    new_query_obj = json.loads(json.dumps(query_obj))
    if new_query_obj["term_category"] == "any":
        new_query_obj["term"] = transform_query_term(new_query_obj["term"])


    record_type = "disease"
    api_name = "disease_search_simple"
    list_id = get_hash_id(api_name, record_type, query_obj)
    cache_coll = "c_usercache"
    #cached_obj = dbh[cache_coll].find_one({"list_id":list_id})
    #if cached_obj != None:
    #    if len(cached_obj["results"]) > 0:
    #        return {"list_id":list_id}

    mongo_query = get_simple_mongo_query(new_query_obj)
    #return mongo_query

    collection = "c_disease"
    record_list = []
    prj_obj = {"record_id":1}
    for obj in dbh[collection].find(mongo_query,prj_obj):
        record_list.append(obj["record_id"])
    #return record_list

    ts_format = "%Y-%m-%d %H:%M:%S %Z%z"
    ts = datetime.datetime.now(pytz.timezone('US/Eastern')).strftime(ts_format)
    cache_coll = "c_usercache"
    list_id = "" if len(record_list) == 0 else list_id
    if len(record_list) != 0:
        cache_info = {
            "query":query_obj,
            "ts":ts,
            "record_type":record_type,
            "search_type":"disease_search_simple"
        }
        cache_hitlist(dbh,list_id,record_list,cache_info,cache_coll,config_obj)
    res_obj = {"list_id":list_id}
    res_obj["query"] = query_obj
    res_obj["resultcount"] = len(record_list)

    return res_obj





def disease_detail(query_obj, config_obj):

    dbh, error_obj = get_mongodb()
    if error_obj != {}:
        return error_obj

    #Collect errors 
    error_list = get_errors_in_query("disease_detail", query_obj, config_obj)
    if error_list != []:
        return {"error_list":error_list}
    collection = "c_disease"

    mongo_query = {"record_id":{"$eq":query_obj["record_id"]}}
    obj = dbh[collection].find_one(mongo_query)
    #check for post-access error, error_list should be empty upto this line
    post_error_list = []
    if obj == None:
        post_error_list.append({"error_code":"non-existent-record"})
        res_obj = {"error_list":post_error_list}
        # check if it is a synonym ID
        disease_id = query_obj["record_id"].upper().replace(".",":")
        q = {"synonyms.id": {"$eq": disease_id}}
        rec_id_list = []
        for doc in dbh[collection].find(q):
            if doc["disease_id"] not in rec_id_list:
                rec_id_list.append(doc["disease_id"])
        if rec_id_list != []:
            res_obj["recommended_id_list"] = rec_id_list
        q = {"unlinked_id_list": {"$eq": disease_id}}
        rec_id_list = []
        for doc in dbh[collection].find(q):
            if doc["disease_id"] not in rec_id_list:
                rec_id_list.append(doc["disease_id"])
        if rec_id_list != []:
            res_obj["unlinked_id_in"] = rec_id_list

        return res_obj

    if "_id" in obj:
        obj.pop("_id")

    if "paginated_tables" in query_obj:
        table_id_list = []
        for o in query_obj["paginated_tables"]:
            if o["table_id"] not in table_id_list:
                table_id_list.append(o["table_id"])
        sec_tables = get_paginated_sections(obj, query_obj, table_id_list, True)
        if "error_list" in sec_tables:
            return sec_tables
        for sec in sec_tables:
            obj[sec] = sec_tables[sec]



    return obj




def disease_search(query_obj, config_obj):

    dbh, error_obj = get_mongodb()
    if error_obj != {}:
        return error_obj


    #Collect errors 
    error_list = get_errors_in_query("disease_search", query_obj,config_obj)
    if error_list != []:
        return {"error_list":error_list}

    record_type = "disease"
    api_name = "disease_search"
    list_id = get_hash_id(api_name, record_type, query_obj)
    
    #Get cached object
    cache_coll = "c_initcache"
    mongo_query = {"list_id":list_id}
    cached_obj = dbh[cache_coll].find_one(mongo_query)
    if cached_obj == None:
        cache_coll = "c_usercache"
        cached_obj = dbh[cache_coll].find_one(mongo_query)

    if cached_obj != None:
        if len(cached_obj["results"]) > 0:
            return {"list_id":list_id, "result_count":cached_obj["total_count"]}




    ts_format = "%Y-%m-%d %H:%M:%S %Z%z"
    ts_list = []
    field2sec = {
        "disease_name":"disease_name",
        "protein_name":"proteins",
        "gene_name":"proteins",
        "tax_name":"species"
    }

    p_list = []
    for p in  query_obj:
        if p not in ["operation","query_type"]:
            ff_list, val_obj = [p], query_obj[p]
            for child_key in []:
                if child_key in val_obj:
                    ff_list.append(child_key)
                    val_obj = val_obj[child_key]
            p_list.append(".".join(ff_list))
    for f in field2sec:
        sec = field2sec[f]
        if p_list == [f]:
            f_parts = f.split(".")
            val = query_obj[f_parts[0]]
            if type(val) is dict:
                for ff in f_parts[1:]:
                    val = val[ff]
            ts_list.append("1a-"+datetime.datetime.now(pytz.timezone('US/Eastern')).strftime(ts_format))
            query_obj_new = {"term":val,"term_category":sec}
            exact_match_flag = True
            res_obj = use_indexed_search("disease_search_simple", query_obj_new,config_obj,exact_match_flag)
            ts_list.append("1b-"+datetime.datetime.now(pytz.timezone('US/Eastern')).strftime(ts_format))
            #return {"tslist":ts_list}
            return res_obj

    ts_list.append("0-"+datetime.datetime.now(pytz.timezone('US/Eastern')).strftime(ts_format))


    query_obj_one, query_obj_two = {}, {}
    for f in query_obj:
        query_obj_one[f] = query_obj[f]

    collection = "c_disease"
    prj_obj = {"record_id":1}
    f_list = list(query_obj.keys())
    for f in f_list:
        if f in ["disease_name"]:
            query_obj_two[f] = query_obj[f]
            query_obj_one.pop(f)
   

    mongo_query_one, mongo_query_two = {}, {}

    record_list_one = []
    f_list = list(query_obj_one.keys())
    if "operation" in f_list:
        f_list.remove("operation")
    #if f_list != []:
    if True:
        mongo_query_one = get_mongo_query(query_obj_one)
        #return mongo_query_one
        for obj in dbh[collection].find(mongo_query_one,prj_obj):
            record_list_one.append(obj["record_id"])


    record_list_two = []
    if query_obj_two != {}:
        mongo_query_two = get_mongo_query(query_obj_two)
        prj_obj["id_list"] = 1
        parent_list, child_list = [], []
        for obj in dbh[collection].find(mongo_query_two,prj_obj):
            parent_list.append(obj["record_id"])
            if "search_type" in query_obj_one:
                if query_obj_one["search_type"] == "hierarchy":
                    for child_id in obj["id_list"]:
                        child_list.append(child_id.lower().replace(":","."))
        record_list_two = list(set(parent_list + child_list))


    record_list = []
    if record_list_one == []:
        record_list = record_list_two
    elif record_list_two == []:
        record_list = record_list_one
    else:
        # by default, take intersection since default operation is AND
        record_list = list(set(record_list_one).intersection(set(record_list_two)))
        #if OR operation
        if "operation" in query_obj_one:
            if query_obj_one["operation"].upper() in ["OR"]:
                record_list = list(set(record_list_one + record_list_two))
    
    #return {"rlist_one":record_list_one, "rlist_two":record_list_two,"rlist":record_list, 
    #    "q_one":mongo_query_one, "q_two":mongo_query_two}

    ts_format = "%Y-%m-%d %H:%M:%S %Z%z"
    ts = datetime.datetime.now(pytz.timezone('US/Eastern')).strftime(ts_format)
    cache_coll = "c_usercache"
    list_id = "" if len(record_list) == 0 else list_id
    if len(record_list) != 0:
        cache_info = {
            "query":query_obj,
            "ts":ts,
            "record_type":record_type,
            "search_type":"disease_search"
        }
        cache_hitlist(dbh,list_id,record_list,cache_info,cache_coll,config_obj)
    res_obj = {"list_id":list_id, "result_count":len(record_list)}
 
    #return {"tslist":ts_list, "mongo_one":mongo_query_one, "mongo_two":mongo_query_two}
    return res_obj




def get_mongo_query(query_obj):


    cond_obj_list = []
    f = "disease_id"
    if f in query_obj:
        val = query_obj[f]
        tmp_list = val.replace(" ", "").split(",")
        qid_list = []
        for qid in tmp_list:
            if qid.strip() != "":
                qid_list.append(qid)
        or_list = [
            {"record_id":{'$in': qid_list}},
            {"disease_id":{'$in': qid_list}},
            {"recommended_name.id":{'$in': qid_list}},
            {"synonyms.id":{'$in': qid_list}}
        ]
        cond_obj_list.append({"$or":or_list})




    f = "disease_name"
    if f in query_obj:
        val = query_obj[f]
        or_list = [
            {"recommended_name.name":{'$regex': val, '$options': 'i'}},
            {"synonyms.name":{'$regex': val, '$options': 'i'}}
        ]
        cond_obj_list.append({"$or":or_list})
 
              
    f = "protein_id"
    if f in query_obj:
        val = query_obj[f]
        cond_obj_list.append({
            "$or":[
                {"proteins.uniprot_canonical_ac":{'$eq': val.upper()}},
                {"proteins.uniprot_ac":{'$eq': val.upper()}},
                {"proteins.uniprot_id":{'$eq': val}},
                {"proteins.refseq_ac":{'$eq': val}}
            ]   
        })   
    f = "tax_id"
    if f in query_obj:
        val = query_obj[f]
        cond_obj_list.append({
            "$or":[
                {"proteins.species.taxid":{'$eq': val}},
                {"glycans.species.taxid":{'$eq': val}}
            ]   
        })   
    f = "tax_name"
    if f in query_obj:
        val = query_obj[f]
        cond_obj_list.append({
            "$or":[
                {"proteins.species.name":{'$regex': val, '$options': 'i'}},
                {"proteins.species.common_name":{'$regex': val, '$options': 'i'}},
                {"proteins.species.glygen_name":{'$regex': val, '$options': 'i'}},
                {"proteins.species.reference_species":{'$regex': val, '$options': 'i'}},
                {"glycans.species.name":{'$regex': val, '$options': 'i'}},
                {"glycans.species.common_name":{'$regex': val, '$options': 'i'}},
                {"glycans.species.glygen_name":{'$regex': val, '$options': 'i'}},
                {"glycans.species.reference_species":{'$regex': val, '$options': 'i'}}
            ]   
        })   
    f = "protein_name"
    if f in query_obj:
        val = query_obj[f]
        cond_obj_list.append({
            "$or":[
                {"proteins.protein_names.name":{'$regex': val, '$options': 'i'}}
            ]
        })
    f = "gene_name"
    if f in query_obj:
        val = query_obj[f]
        cond_obj_list.append({
            "$or":[
                {"proteins.gene_names.name":{'$regex': val, '$options': 'i'}}
            ]
        })
    f = "glycan_id"
    if f in query_obj:
        val = query_obj[f]
        cond_obj_list.append({
            "$or":[
                {"glycans.glytoucan_ac":{'$eq': val.upper()}}
            ]
        })
    f = "glycan_name"
    if f in query_obj:
        val = query_obj[f]
        cond_obj_list.append({
            "$or":[
                {"glycans.names.name":{'$regex': val, '$options': 'i'}}
            ]
        })
    f = "biomarker_id"
    if f in query_obj:
        val = query_obj[f]
        cond_obj_list.append({
            "$or":[
                {"biomarkers.biomarker_id":{'$eq': val.upper()}},
                {"biomarkers.biomarker_canonical_id":{'$eq': val.upper()}}
            ]
        })
    f = "biomarker_type"
    if f in query_obj:
        val = query_obj[f]
        cond_obj_list.append({
            "$or":[
                {"biomarkers.best_biomarker_role.role":{'$eq': val}}
            ]
        })
    f = "biomarker_component"
    if f in query_obj:
        val = query_obj[f]
        cond_obj_list.append({
            "$or":[
                {"biomarkers.biomarker_component.assessed_biomarker_entity.recommended_name":{'$regex': val, '$options': 'i'}},
                {"biomarkers.biomarker_component.assessed_biomarker_entity.synonyms":{'$regex': val, '$options': 'i'}},
                {"biomarkers.biomarker_component.biomarker":{'$regex': val, '$options': 'i'}},
                {"biomarkers.biomarker_component.assessed_biomarker_entity_id":{'$regex': val, '$options': 'i'}},
                {"biomarkers.biomarker_component.evidence.id":{'$regex': val, '$options': 'i'}}
            ]
        })

    
         
    operation = query_obj["operation"].lower() if "operation" in query_obj else "and"
    mongo_query = {}
    mongo_query = cond_obj_list[0] if len(cond_obj_list) == 1 else mongo_query
    mongo_query = { "$"+operation+"": cond_obj_list } if len(cond_obj_list) > 1 else mongo_query

       
 
    return mongo_query











def get_simple_mongo_query(query_obj):


    query_term = query_obj["term"]
    cond_objs = []
    if query_obj["term_category"] == "any":
        return {'$text': { '$search': query_term}}
    elif query_obj["term_category"] == "disease":
        cond_objs = [
            {"recommended_name.id":{'$regex': query_term, '$options': 'i'}},
            {"recommended_name.name":{'$regex': query_term, '$options': 'i'}},
            {"synonyms.id":{'$regex': query_term, '$options': 'i'}},
            {"synonyms.name":{'$regex': query_term, '$options': 'i'}}
        ]
    elif query_obj["term_category"] == "protein":
        cond_objs = [
            {"proteins.uniprot_canonical_ac":{'$regex': query_term, '$options': 'i'}},
            {"proteins.uniprot_ac":{'$regex': query_term, '$options': 'i'}},
            {"proteins.uniprot_id":{'$regex': query_term, '$options': 'i'}},
            {"proteins.refseq_ac":{'$regex': query_term, '$options': 'i'}},
            {"proteins.protein_names.name":{'$regex': query_term, '$options': 'i'}},
            {"proteins.gene_names.name":{'$regex': query_term, '$options': 'i'}}
        ]
    elif query_obj["term_category"] == "glycan":
        cond_objs = [
            {"glycans.glytoucan_ac":{'$regex': query_term, '$options': 'i'}},
            {"glycans.names":{'$regex': query_term, '$options': 'i'}}
        ]
    elif query_obj["term_category"] == "organism":
        cond_objs = [
            {"proteins.species.taxid":{'$regex': query_term, '$options': 'i'}},
            {"proteins.species.name":{'$regex': query_term, '$options': 'i'}},
            {"proteins.species.common_name":{'$regex': query_term, '$options': 'i'}},
            {"proteins.species.glygen_name":{'$regex': query_term, '$options': 'i'}},
            {"proteins.species.reference_species":{'$regex': query_term, '$options': 'i'}},
            {"glycans.species.taxid":{'$regex': query_term, '$options': 'i'}},
            {"glycans.species.name":{'$regex': query_term, '$options': 'i'}},
            {"glycans.species.common_name":{'$regex': query_term, '$options': 'i'}},
            {"glycans.species.glygen_name":{'$regex': query_term, '$options': 'i'}},
            {"glycans.species.reference_species":{'$regex': query_term, '$options': 'i'}}
        ]
    elif query_obj["term_category"] == "biomarker":
        cond_objs = [
            {"biomarkers.biomarker_id":{'$regex': query_term, '$options': 'i'}},
            {"biomarkers.biomarker_canonical_id":{'$regex': query_term, '$options': 'i'}},
            {"biomarkers.biomarker_component.assessed_biomarker_entity.recommended_name":{'$regex': query_term, '$options': 'i'}},
            {"biomarkers.biomarker_component.assessed_biomarker_entity.synonyms.synonym":{'$regex': query_term, '$options': 'i'}},
            {"biomarkers.biomarker_component.biomarker":{'$regex': query_term, '$options': 'i'}},
            {"biomarkers.biomarker_component.assessed_biomarker_entity_id":{'$regex': query_term, '$options': 'i'}},
            {"biomarkers.biomarker_component.evidence.id":{'$regex': query_term, '$options': 'i'}}
        ]


 
    mongo_query = {} if cond_objs == [] else { "$or": cond_objs }

    return mongo_query



