import os
import string
import random
import hashlib
import json
import datetime,time
import pytz
import re
from collections import OrderedDict
from bson import json_util, ObjectId

from glygen.db import get_mongodb
from glygen.util import cache_record_list, clean_obj, extract_name, get_errors_in_query, order_obj, get_paginated_sections

    
def glycan_search_init(config_obj):
   
    dbh, error_obj = get_mongodb()
    if error_obj != {}:
        return error_obj

    error_list = get_errors_in_query("glycan_searchinit",{}, config_obj)
    if error_list != []:
        return {"error_list":error_list}


    collection = "c_searchinit"
    res_obj =  dbh[collection].find_one({})

    return res_obj["glycan"]



def glycan_search_simple(query_obj, config_obj):

    dbh, error_obj = get_mongodb()
    if error_obj != {}:
        return error_obj


    #Collect errors 
    error_list = get_errors_in_query("glycan_search_simple", query_obj, config_obj)
    if error_list != []:
        return {"error_list":error_list}


    mongo_query = get_simple_mongo_query(query_obj)
    #return {"error_list":[{"error":mongo_query}]}
    #mongo_query = {"byonic": {"$options": "i", "$regex": "Hex\(5\)"}}
    #return mongo_query

    collection = "c_glycan"
    record_list = []
    record_type = "glycan"
    prj_obj = {"glytoucan_ac":1}
    for doc in dbh[collection].find(mongo_query,prj_obj):
        record_list.append(doc["glytoucan_ac"])

    ts_format = "%Y-%m-%d %H:%M:%S %Z%z"
    ts = datetime.datetime.now(pytz.timezone('US/Eastern')).strftime(ts_format)
    cache_coll = "c_cache"
    list_id = ""
    if len(record_list) != 0:
        hash_str = record_type + "_" + json.dumps(query_obj)
        hash_obj = hashlib.md5(hash_str.encode('utf-8'))
        list_id = hash_obj.hexdigest()
        cache_info = {
            "query":query_obj,
            "ts":ts,
            "record_type":record_type,
            "search_type":"search_simple"
        }
        cache_record_list(dbh,list_id,record_list,cache_info,cache_coll,config_obj)
    res_obj = {"list_id":list_id}

    return res_obj




def glycan_search(query_obj, config_obj):

    dbh, error_obj = get_mongodb()
    if error_obj != {}:
        return error_obj


    #Clean query object
    key_list = list(query_obj.keys())
    for key in key_list:
        flag_list = []
        #flag_list.append(key in ["query_type", "operation"])
        flag_list.append(str(query_obj[key]).strip() == "")
        flag_list.append(query_obj[key] == [])
        flag_list.append(query_obj[key] == {})
        if True in flag_list:
            query_obj.pop(key)

    #Collect errors 
    error_list = get_errors_in_query("glycan_search", query_obj, config_obj)
    if error_list != []:
        return {"error_list":error_list}

    if "organism" in query_obj:
        if "operation" not in query_obj["organism"]:
            return {"error_list":[{"error_code":"missing-parameter", 
                "field":"organism.operation"}]}


    residue_list = []
    for o in dbh["c_searchinit"].find_one({})["glycan"]["composition"]:
        residue_list.append(o["residue"])


    #If residue is not in query, add it with default range in query
    seen = {}
    default_min, default_max = 0, 0
    if "composition" in query_obj:
        for o in query_obj["composition"]:
            res = o["residue"]
            seen[res] = True
            if res == "default":
                default_min, default_max = o["min"], o["max"]
                query_obj["composition"].remove(o)

        for res in residue_list:
            if res not in seen:
                o = {"residue":res, "min":default_min, "max":default_max}
                query_obj["composition"].append(o)
        
    mongo_query = get_mongo_query(query_obj)
    #return mongo_query

    collection = "c_glycan"
    cache_collection = "c_cache"

    i = 0
    results = []
    prj_obj = {"glytoucan_ac":1, "subsumption":1, "composition":1,"composition_expanded":1, "glycan_identifier":1,"crossref.id":1}
    doc_list = []
    for doc in dbh[collection].find(mongo_query,prj_obj):
        comp_flag_list = []
        for k in ["composition", "composition_expanded"]:
            if k in query_obj:
                if query_obj[k] != []:
                    flag = passes_composition_filter(doc["glytoucan_ac"], doc[k],k, query_obj)
                    comp_flag_list.append(flag)
        if False in comp_flag_list:
            continue
        doc_list.append(doc)


    #Add additional glycan objects related to hits by subsumption
    if "glycan_identifier" in query_obj:
        if "subsumption" in query_obj["glycan_identifier"]:
            rel_type = query_obj["glycan_identifier"]["subsumption"].lower()
            if rel_type != "none": 
                hit_list = []
                for doc in doc_list:
                    hit_list.append(doc["glytoucan_ac"])
                seen_id = {}
                extra_doc_list = []
                for doc in doc_list:
                    for o in doc["subsumption"]:
                        rel = o["relationship"].lower()
                        tv = rel == rel_type
                        tv = True if rel_type == "any" else tv
                        if tv and o["related_accession"] not in hit_list:
                            seen_id[o["related_accession"]] = True
                for glytoucan_ac in seen_id.keys():
                    doc = dbh[collection].find_one({"glytoucan_ac":glytoucan_ac},prj_obj)
                    extra_doc_list.append(doc)
                doc_list += extra_doc_list


    record_list = []
    record_type = "glycan"
    seen_id = {}
    for doc in doc_list:
        if doc == None:
            continue
        record_list.append(doc["glytoucan_ac"])
        seen_id[doc["glytoucan_ac"]] = True
        for obj in doc["crossref"]:
            seen_id[obj["id"]] = True


    unmapped_obj_list = []
    redundancy_dict = {}
    if "glycan_identifier" in query_obj:
        if "glycan_id" in query_obj["glycan_identifier"]:
            qid_list = get_qid_list(query_obj["glycan_identifier"]["glycan_id"])
            for qid in qid_list:
                if qid not in seen_id:
                    unmapped_obj_list.append({"input_id":qid, "reason":"ID not found"})
                if qid_list.count(qid) > 1:
                    redundancy_dict[qid] = qid_list.count(qid)

    for qid in redundancy_dict:
        for i in range(redundancy_dict[qid] - 1):
            unmapped_obj_list.append({"input_id":qid, "reason":"Duplicate ID"})




    ts_format = "%Y-%m-%d %H:%M:%S %Z%z"
    ts = datetime.datetime.now(pytz.timezone('US/Eastern')).strftime(ts_format)
    cache_coll = "c_cache"
    list_id = ""
    if len(record_list) != 0:
        hash_str = record_type + "_" + json.dumps(query_obj)
        hash_obj = hashlib.md5(hash_str.encode('utf-8'))
        list_id = hash_obj.hexdigest()
        cache_info = {
            "query":query_obj,
            "ts":ts, 
            "record_type":record_type, 
            "search_type":"search",
        }
        if unmapped_obj_list != []:
            cache_info["batch_info"] = {"unmapped":unmapped_obj_list}
        cache_record_list(dbh,list_id,record_list,cache_info,cache_coll,config_obj)
    res_obj = {"list_id":list_id}

    return res_obj
    






def glycan_detail(query_obj, config_obj):

    dbh, error_obj = get_mongodb()
    if error_obj != {}:
        return error_obj


    #Collect errors 
    error_list = get_errors_in_query("glycan_detail", query_obj, config_obj)
    if error_list != []:
        return {"error_list":error_list}
    collection = "c_glycan"


    q = {
        "$and":[ 
            {"record_id":{'$eq': query_obj["glytoucan_ac"].upper()}},
            {"recordtype":{"$eq": "glycan"}}
        ]
    }
    history_obj = dbh["c_idtrack"].find_one(q)

    glytoucan_ac = query_obj["glytoucan_ac"].upper()
    mongo_query = {"glytoucan_ac":{'$eq': glytoucan_ac}}
    obj = dbh[collection].find_one(mongo_query)
    
    #check for post-access error, error_list should be empty upto this line
    post_error_list = []
    if obj == None:
        post_error_list.append({"error_code":"non-existent-record"})
        res_obj = {"error_list":post_error_list}
        if history_obj != None:
            res_obj["reason"] = history_obj["history"][-1]
        else:
            res_obj["reason"] = {"type":"invalid","description": "Invalid accession"}
        return res_obj

   
    # Get section objects if this record was batched 
    q = {"batchid": 1, "recordid": glytoucan_ac, "recordtype": "glycan"}
    batch_doc = dbh["c_batch"].find_one(q)
    if batch_doc != None:
        #return list(batch_doc["sections"].keys())
        for sec in batch_doc["sections"]:
            if sec in obj:
                if len(batch_doc["sections"][sec]) > 1000:
                    obj[sec] += batch_doc["sections"][sec][:1000]
                else:
                    obj[sec] += batch_doc["sections"][sec]


    url = config_obj["urltemplate"]["glytoucan"] % (obj["glytoucan_ac"])
    obj["glytoucan"] = {"glytoucan_ac":obj["glytoucan_ac"], "glytoucan_url":url}
    obj["history"] = history_obj["history"] if history_obj != None else []


    #Remove 0 count residues
    tmp_list = []
    for o in obj["composition"]:
        if o["count"] > 0:
            tmp_list.append(o)
    obj["composition"] = tmp_list


    if "paginated_tables" in query_obj:
        table_id_list = []
        for o in query_obj["paginated_tables"]:
            if o["table_id"] not in table_id_list:
                table_id_list.append(o["table_id"])
        sec_tables = get_paginated_sections(obj, query_obj, table_id_list)
        if "error_list" in sec_tables:
            return sec_tables
        for sec in sec_tables:
            obj[sec] = sec_tables[sec]
    
    clean_obj(obj, config_obj["removelist"]["c_glycan"], "c_glycan")

    if "enzyme" in obj:
        for o in obj["enzyme"]:
            if "gene_url" in o:
                o["gene_link"] = o["gene_url"]

    
    return order_obj(obj, config_obj["objectorder"]["glycan"])


def glycan_image(query_obj, data_path):
  
    dbh, error_obj = get_mongodb()
    if error_obj != {}:
        return error_obj

    init_obj = dbh["c_init"].find_one({})
    ver = init_obj["dataversion"]
    img_path = data_path + "/releases/data/v-%s/glycanimages_snfg/" % (ver)
    
    img_file =  img_path + query_obj["glytoucan_ac"].upper() + ".png"
    if os.path.isfile(img_file) == False:
        img_file = img_path +  "G0000000.png" 
    return img_file


def glycan_image_svg(query_obj, data_path):

    dbh, error_obj = get_mongodb()
    if error_obj != {}:
        return error_obj

    init_obj = dbh["c_init"].find_one({})
    ver = init_obj["dataversion"]
    img_path = data_path + "/releases/data/v-%s/glycanimages_snfg_svg/" % (ver)
    img_file =  img_path + query_obj["glytoucan_ac"].upper() + ".svg" 
    if os.path.isfile(img_file) == False:
        img_file = img_path +  "G0000000.svg"
           
    return img_file





def get_simple_mongo_query(query_obj):


    query_term = query_obj["term"]
    cond_objs = []
    if query_obj["term_category"] == "any":
        tv, q = is_glycan_composition(query_obj["term"])
        if tv == True:
            return q
        return {'$text': { '$search': query_term}}
    elif query_obj["term_category"] == "glycan":
        tv, q = is_glycan_composition(query_obj["term"])
        if tv == True:
            return q
        cond_objs.append({"glytoucan_ac":{'$regex': query_obj["term"], '$options': 'i'}})
        qval = query_obj["term"].replace("(", "\\(").replace(")", "\\)")
        #cond_objs.append({"iupac":{'$regex': query_obj["term"], '$options': 'i'}})
        #cond_objs.append({"wurcs":{'$regex': query_obj["term"], '$options': 'i'}})
        #cond_objs.append({"glycoct":{'$regex': query_obj["term"], '$options': 'i'}})
        cond_objs.append({"iupac":{'$regex': qval, '$options': 'i'}})
        cond_objs.append({"wurcs":{'$regex': qval, '$options': 'i'}})
        cond_objs.append({"glycoct":{'$regex': qval, '$options': 'i'}})
        cond_objs.append({"byonic":{'$regex': qval, '$options': 'i'}})
        cond_objs.append({"names.name": {'$regex': qval,'$options': 'i'}})
    elif query_obj["term_category"] == "protein":
        cond_objs.append({"glycoprotein.uniprot_canonical_ac":{'$regex': query_obj["term"], '$options': 'i'}})
        cond_objs.append({"glycoprotein.protein_name":{'$regex': query_obj["term"], '$options': 'i'}})
    elif query_obj["term_category"] == "enzyme":
        cond_objs.append({"enzyme.uniprot_canonical_ac":{'$regex': query_obj["term"], '$options': 'i'}})
        cond_objs.append({"enzyme.protein_name":{'$regex': query_obj["term"], '$options': 'i'}})
        cond_objs.append({"enzyme.gene":{'$regex': query_obj["term"], '$options': 'i'}})
    elif query_obj["term_category"] == "organism":
        cond_objs.append({"species.name":{'$regex': query_obj["term"], '$options': 'i'}})
    
    
    mongo_query = {} if cond_objs == [] else { "$or": cond_objs }
    return mongo_query


def get_qid_list(q):
    q = q.replace("[", "\\[")
    q = q.replace("[", "\\[")
    q = q.replace("]", "\\]")
    q = q.replace("(", "\\(")
    q = q.replace(")", "\\)")
    q = q.replace("[", "\\[")
    qid_list = q.replace(" ", "").split(",")
    return qid_list


def get_mongo_query(query_obj):

    cond_objs = []
    #glytoucan_ac
    if "glycan_identifier" in query_obj:
        if "glycan_id" in query_obj["glycan_identifier"]:
            qid_list = get_qid_list(query_obj["glycan_identifier"]["glycan_id"])
            #qval = "^%s$" % (q)
            cond_objs.append(
                {
                "$or":[
                    {"glytoucan_ac":{"$in": qid_list}},
                    {"crossref.id":{"$in": qid_list}}
                ]
                }
            )


    #glycan_name
    if "glycan_name" in query_obj:
        qval = query_obj["glycan_name"].replace("(", "\\(").replace(")", "\\)")
        q = {"names.name": {'$regex': qval, '$options': 'i'}}
        cond_objs.append(q)

    
    #mass
    if "mass" in query_obj:
        mass_field = "mass_pme" if query_obj["mass_type"].lower() != "native" else "mass"
        if "min" in query_obj["mass"]:
            cond_objs.append({mass_field:{'$gte': query_obj["mass"]["min"]}})
        if "max" in query_obj["mass"]:
            cond_objs.append({mass_field:{'$lte': query_obj["mass"]["max"]}})
    
    #number_monosaccharides
    if "number_monosaccharides" in query_obj:
        if "min" in query_obj["number_monosaccharides"]:
            cond_objs.append({"number_monosaccharides":{'$gte': query_obj["number_monosaccharides"]["min"]}})
        if "max" in query_obj["number_monosaccharides"]:
            cond_objs.append({"number_monosaccharides":{'$lte': query_obj["number_monosaccharides"]["max"]}})

    #subsumption
    if "subsumption" in query_obj:
        rel, rel_ac = "any", ""
        if "relationship" in query_obj["subsumption"]:
            rel = query_obj["subsumption"]["relationship"]
        if "related_ac" in query_obj["subsumption"]:
            rel_ac = query_obj["subsumption"]["related_ac"]
        if rel_ac != "":
            q_one = {
                "$and":[
                    {"subsumption.relationship":{'$regex':rel, '$options': 'i'}},
                    {"subsumption.id":{'$regex':rel_ac, '$options': 'i'}}
                ]
            }
            q_two = {"subsumption.id":{'$regex':rel_ac, '$options': 'i'}}
            q = q_two if rel == "any" else q_one
            cond_objs.append(q)

    #biomarker
    if "biomarker" in query_obj:
        if "id" in query_obj["biomarker"]:
            if len(query_obj["biomarker"]["id"]) > 0:
                o = {"biomarkers.biomarker_id": {'$regex': query_obj["biomarker"]["id"], '$options': 'i'}}
                cond_objs.append(o)
        if "name" in query_obj["biomarker"]:
            if len(query_obj["biomarker"]["name"]) > 0:
                o = {"biomarkers.assessed_biomarker_entity":{'$regex':query_obj["biomarker"]["name"],'$options':'i'}}
                cond_objs.append(o)
        if "type" in query_obj["biomarker"]:
            if len(query_obj["biomarker"]["type"]) > 0:
                o = {"biomarkers.instances.best_biomarker_type": {'$regex': query_obj["biomarker"]["type"], '$options': 'i'}}
                cond_objs.append(o)
        if "disease_id" in query_obj["biomarker"]:
            if len(query_obj["biomarker"]["disease_id"]) > 0:
                disease_id = query_obj["biomarker"]["disease_id"]
                or_list = [
                    {"biomarkers.instances.disease.recommended_name.id":{'$regex':disease_id,'$options':'i'}},
                    {"biomarkers.instances.disease.synonyms.id":{'$regex':disease_id,'$options':'i'}},
                ]
                cond_objs.append({'$or':or_list})
        if "disease_name" in query_obj["biomarker"]:
            if len(query_obj["biomarker"]["disease_name"]) > 0:
                disease_name = query_obj["biomarker"]["disease_name"]
                or_list = [
                    {"biomarkers.instances.disease.recommended_name.name":{'$regex':disease_name,'$options':'i'}},
                    {"biomarkers.instances.disease.synonyms.name":{'$regex':disease_name,'$options':'i'}}
                ]
                cond_objs.append({'$or':or_list})

    
    #organism
    if "organism" in query_obj:
        cat_q = ""
        if "annotation_category" in query_obj["organism"]:
            cat_q = {'$regex': query_obj["organism"]["annotation_category"], '$options': 'i'}
        if "organism_list" in query_obj["organism"]:
            obj_list = []
            for o in query_obj["organism"]["organism_list"]:
                or_list = []
                if "id" in o:
                    if o["id"] > 0:
                        tmp_q = {
                            "species":
                            { "$elemMatch": { "taxid": {"$eq":o["id"]}}}
                        }
                        if cat_q != "":
                            tmp_q["species"]["$elemMatch"]["annotation_category"] = cat_q
                        or_list.append(tmp_q)
                if "name" in o:
                    if o["name"].strip() != "":
                        tmp_q = {
                            "species":
                            { "$elemMatch": { "name": {"$regex":o["name"], '$options':'i'}}}
                        }
                        if cat_q != "":
                            tmp_q["species"]["$elemMatch"]["annotation_category"] = cat_q
                        or_list.append(tmp_q)
                if or_list != []:
                    or_query = {"$or":or_list}
                    obj_list.append(or_query)

            if obj_list != []:
                operation = query_obj["organism"]["operation"]
                q_one = {"$"+operation+"":obj_list}
                cond_objs.append(q_one)



    #protein_identifier
    if "protein_identifier" in query_obj:
        cond_objs.append(
            {"$or":[
                {"glycoprotein.uniprot_canonical_ac": {'$regex': query_obj["protein_identifier"], '$options': 'i'}},
                {"glycoprotein.gene_name": {'$regex': query_obj["protein_identifier"], '$options': 'i'}}
                ]
            }
        )
    #glycan_motif
    if "glycan_motif" in query_obj:
        cond_objs.append(
            {
                "$or":[
                    {"motifs.name": {'$regex': query_obj["glycan_motif"], '$options': 'i'}}
                    ,{"motifs.synonym": {'$regex': query_obj["glycan_motif"], '$options': 'i'}}
                ]
            }
        )
    #glycan_type 
    if "glycan_type" in query_obj:
        cond_objs.append({"classification.type.name": {'$regex': query_obj["glycan_type"], '$options': 'i'}})
     
    #pmid
    if "pmid" in query_obj:
        cond_objs.append({"publication.reference.id" : {'$regex': query_obj["pmid"], '$options': 'i'}})

    #id_namespace
    if "id_namespace" in query_obj:
        cond_objs.append({"crossref.database" : {'$regex': query_obj["id_namespace"], '$options': 'i'}})

    #binding_protein_id
    if "binding_protein_id" in query_obj:
        q = {"interactions.interactor_id":{'$regex': query_obj["binding_protein_id"], '$options': 'i'}}
        cond_objs.append(q)

    #glycan_subtype
    if "glycan_subtype" in query_obj:
        cond_objs.append({"classification.subtype.name": {'$regex': query_obj["glycan_subtype"], 
                                                            '$options': 'i'}})
    #enzyme
    if "enzyme" in query_obj:
        if "id" in query_obj["enzyme"]:
            cond_objs.append(
                {"$or":[
                        {"enzyme.gene": {'$regex': query_obj["enzyme"]["id"], '$options': 'i'}},
                        {"enzyme.uniprot_canonical_ac": {'$regex': query_obj["enzyme"]["id"], '$options': 'i'}}
                    ]
                })



    if "composition" in query_obj:
        for o in query_obj["composition"]:
            cond_objs.append({"composition.residue": {'$eq': o["residue"]}})
            #if o["max"] > 0:
            #    cond_objs.append({"composition.residue": {'$eq': o["residue"]}})
            #else:
            #    cond_objs.append({"composition.residue": {'$ne': o["residue"]}})

    operation = query_obj["operation"].lower() if "operation" in query_obj else "and"
    mongo_query = {} if cond_objs == [] else { "$"+operation+"": cond_objs }

    return mongo_query










def passes_composition_filter(glytoucan_ac, comp_obj, comp_field, query_obj):

    tv = []
    n_cond = 0
    for q in query_obj[comp_field]:
        q_res, q_min, q_max = q["residue"], q["min"], q["max"]
        if q_max >= 0:
            n_cond += 1
            for o in comp_obj:
                o_res, o_count = o["residue"], o["count"]
                if o_res == q_res and o_count >= q_min and o_count <= q_max:
                    tv.append(True)
                    break
   
    r_value = len(tv) == n_cond and list(set(tv)) == [True]

    return r_value



def is_glycan_composition(term):
    term = term.strip().replace(" ", "")
    res_str = re.sub(r"[(,)]", " ", term)
    tmp_list_one, tmp_list_two = [], []
    w_list = res_str.strip().split(" ")
    if len(w_list)%2 != 0:
        return False, []
    for i in range(0, len(w_list) -1):
        if i%2 == 0:
            s = w_list[i]
            ss = w_list[i+1]
            f = s.isalpha() and ss.isdigit()
            tmp_list_one.append(f)
            cmp = "%s\(%s\)" % (s, ss)
            #o = {"$text": { "$search": cmp}}
            o = {"byonic": { "$regex": cmp, "$options":"i"}}
            tmp_list_two.append(o)

    return list(set(tmp_list_one)) == [True], {"$and":tmp_list_two}


