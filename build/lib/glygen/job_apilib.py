import os
import string
import random
import hashlib
import json
import datetime,time
import bcrypt
import base64
import subprocess
import pytz
from collections import OrderedDict
from bson.objectid import ObjectId


from glygen.libgly import load_species_info
from glygen.db import get_mongodb
from glygen.util import get_errors_in_query, sort_objects, cache_record_list




def job_init(config_obj, data_path):

    dbh, error_obj = get_mongodb()
    if error_obj != {}:
        return error_obj
    init_obj = dbh["c_init"].find_one({})

    #Set number of jobs allowed
    cmd = "%s -S %s" % (config_obj["jobinfo"]["tspath"], config_obj["jobinfo"]["maxjobs"])
    x = subprocess.getoutput(cmd)


    res_obj = {}
    for k_one in config_obj["jobinfo"]:
        if type(config_obj["jobinfo"][k_one]) is dict:
            if "paramlist" in config_obj["jobinfo"][k_one]:
                if k_one not in res_obj:
                    res_obj[k_one] = {"paramlist":[]}
                for obj in config_obj["jobinfo"][k_one]["paramlist"]:
                    for k in ["cmdflag","type"]:
                        if k in obj:
                            obj.pop(k)
                    res_obj[k_one]["paramlist"].append(obj)


    species_obj = {}
    in_file = data_path + "/releases/data/v-%s/misc/species_info.csv" % (init_obj["dataversion"])
 
    load_species_info(species_obj, in_file)
    opt_list = [
        {"value":"canonicalsequences_all", "label":"All species"}        
    ]
    species_list = []
    for k in species_obj:
        obj = species_obj[k]
        if obj["short_name"] not in species_list and obj["is_reference"] == "yes":
            o = {"value":"canonicalsequences_%s" % (obj["short_name"]),"label":obj["long_name"]}
            opt_list.append(o) 
            species_list.append(obj["short_name"])


    for obj in res_obj["blastp"]["paramlist"]:
        if obj["id"] == "targetdb":
            obj["optlist"] = opt_list

    return res_obj


def job_addnew(query_obj, config_obj, data_path, server):


    dbh, error_obj = get_mongodb()
    if error_obj != {}:
        return error_obj
    init_obj = dbh["c_init"].find_one({})
    release_dir = data_path + "/releases/data/v-%s/" % (init_obj["dataversion"])

    validation_obj, error_list = validate_input(query_obj, config_obj, release_dir, server)
    if error_list != []:
        return {"error_list":error_list}

    #return query_obj
    #return validation_obj

    res_obj = {}
    try:
        query_obj["jobid"] = 1
        if dbh["c_job"].find_one({"jobid":1}) != None:
            agg_obj = {"$group":{"_id":"","max_id":{"$max":"$jobid"}}}
            res = list(dbh["c_job"].aggregate([agg_obj]))
            query_obj["jobid"] = res[0]["max_id"] + 1

        q_obj = {}
        for p in query_obj:
            if p not in ["cmd", "status", "jobid"]:
                q_obj[p] = query_obj[p]

        #old_doc = dbh["c_job"].find_one(q_obj)
        old_doc = None
        if old_doc != None:
            status_obj = update_job_status(dbh, old_doc, config_obj)
            if "error_list" in status_obj:
                return status_obj
            res_obj = {"submission":"old", "status":status_obj, "jobid":old_doc["jobid"]}
        else:
            in_dir = data_path + "/userdata/" + server + "/jobs/"
            in_dir += str(query_obj["jobid"]) + "/"
            cmd = "mkdir -p " + in_dir
            x = subprocess.getoutput(cmd)
            in_filename = config_obj["jobinfo"][query_obj["jobtype"]]["input_files"][0]["name"]
            out_filename = config_obj["jobinfo"][query_obj["jobtype"]]["output_files"][0]["name"]
            in_file = in_dir + in_filename
            out_file = in_dir + out_filename
            
            
            with open(in_file, "w") as FW:
                if query_obj["jobtype"] in ["structure_search"]:
                    FW.write("%s\n" % (json.dumps(json.loads(validation_obj["buffer"]))))
                else:
                    FW.write("%s\n" % (validation_obj["buffer"]))

            if "incmdflag" in config_obj["jobinfo"][query_obj["jobtype"]]:
                in_cmdflag = config_obj["jobinfo"][query_obj["jobtype"]]["incmdflag"]
                query_obj["cmd"] += " %s %s" % (in_cmdflag, in_file)
            if "outcmdflag" in config_obj["jobinfo"][query_obj["jobtype"]]:
                out_cmdflag = config_obj["jobinfo"][query_obj["jobtype"]]["outcmdflag"]
                query_obj["cmd"] += " %s %s" % (out_cmdflag, out_file)
            
            job_lbl = "%s_%s" % (query_obj["jobtype"], query_obj["jobid"])
            cmd = "%s -E -L %s %s" % (config_obj["jobinfo"]["tspath"],job_lbl, query_obj["cmd"])
            
            query_obj["cmdin"] = cmd
            cmdout = subprocess.getoutput(cmd)
            query_obj["cmdout"] = cmdout
            query_obj["tsid"] = cmdout.split(" ")[0]
            query_obj["status"] = get_job_status(query_obj["tsid"] , config_obj)
            inserted_id = dbh["c_job"].insert(query_obj)

            out_file = in_dir + "/jobinfo.json"
            with open(out_file, "w") as FW:
                if "_id" in query_obj:
                    query_obj.pop("_id")
                FW.write("%s\n" % (json.dumps(query_obj, indent=4)))

            res_obj = {"submission":"new", "status":query_obj["status"], "jobid":query_obj["jobid"]}
    except Exception as e:
        res_obj = {"error_list":[{"error_code":str(e)}]}

    return res_obj


def job_queue(query_obj, config_obj):

    dbh, error_obj = get_mongodb()
    if error_obj != {}:
        return error_obj


    res_obj = {
        "header":["ID","State","Output","E-Level","Times(r/u/s)", "Command [run=3/3]"], 
        "rows":[]    
    }
    try:
        cmd = "%s" % (config_obj["jobinfo"]["tspath"])
        for line in subprocess.getoutput(cmd).split("\n")[1:]:
            row = []
            row.append(line[0:5].strip())
            row.append(line[5:16].strip())
            row.append(line[16:37].strip())
            row.append(line[37:46].strip())
            row.append(line[46:61].strip())
            row.append(line[61:].strip())
            res_obj["rows"].append(row)

    except Exception as e:
        res_obj = {"error_list":[{"error_code":str(e)}]}

    return res_obj


def job_results(query_obj, config_obj):

    
    res_obj = {}
    try:
        job_dir = config_obj[config_obj["server"]]["pathinfo"]["userdata"]
        job_dir +=  str(query_obj["jobid"]) + "/"
        in_file = job_dir + "jobinfo.json"
        if os.path.isfile(in_file) == False:
            return {"error_list":[{"error_code":"job submission does not exist"}]}

        job_info = json.loads(open(in_file, "r").read())
        job_type = job_info["jobtype"]
        status_obj = get_job_status(job_info["tsid"] , config_obj)

        out_file = job_dir + config_obj["jobinfo"][job_type]["output_files"][0]["name"]
        res_obj = {"list_id":""}
        if status_obj["status"] == "finished":
            if job_type == "blastp":
                res_obj = parse_blastp_ouput(out_file, config_obj)
            elif job_type in ["structure_search"]:
                res_obj = parse_structure_search_ouput(out_file, config_obj, job_info)
        if "error" in status_obj:
            res_obj["error"] = status_obj["error"]
        res_obj["status"] = status_obj["status"] if "error_list" not in res_obj else "error"
        res_obj["jobtype"] = job_info["jobtype"]
        res_obj["parameters"] = job_info["parameters"]

    except Exception as e:
        res_obj = {"error_list":[{"error_code":str(e)}]}

    return res_obj




def parse_structure_search_ouput(out_file, config_obj, job_info):


    dbh, error_obj = get_mongodb()
    if error_obj != {}:
        return error_obj

    res_obj = {"list_id":""} 
    row_list = []
    if os.path.isfile(out_file) == True:
        out_json = json.loads(open(out_file, "r").read())
        if "error" in out_json:
            return {"error_list":[{"error_code":out_json["error"][0]}]}
        else:
            if "result" in out_json:
                row_list = out_json["result"]
            else:
                return {"error_list":[{"error_code":"bad resuls object from structure_search"}]}

    record_list = []
    for row in row_list:
        if row[1] == True:
            record_list.append(row[0])



    ts_format = "%Y-%m-%d %H:%M:%S %Z%z"
    ts = datetime.datetime.now(pytz.timezone('US/Eastern')).strftime(ts_format)
    cache_coll = "c_cache"
    list_id = ""
    record_type = "glycan"
    if len(record_list) != 0:
        hash_str = record_type + "_" + json.dumps(job_info)
        hash_obj = hashlib.md5(hash_str.encode('utf-8'))
        list_id = hash_obj.hexdigest()
        cache_info = {
            "query":job_info,
            "ts":ts,
            "record_type":record_type,
            "search_type":job_info["jobtype"]
        }
        cache_record_list(dbh,list_id,record_list,cache_info,cache_coll,config_obj)
    res_obj["list_id"] = list_id
    return res_obj



def parse_blastp_ouput(out_file, config_obj):
   

    dbh, error_obj = get_mongodb()
    if error_obj != {}:
        return error_obj

    res_obj_dict = {}
    hsp_idx, aln_idx = -1, -1
    query_open = False
    sbj_id = ""
    query_id = ""
    raw = ""
    with open(out_file, "r") as FR:
        for line in FR:
            raw += line
            if line[0:7] == "Query= ":
                query_id = line.strip().split(" ")[-1]
            elif line[0] == ">":
                sbj_id = line[1:].split(" ")[0]
                res_obj_dict[sbj_id] = {"hsp_list":[]}
                hsp_idx = -1
            elif line.find("Score = ") != -1:
                res_obj_dict[sbj_id]["hsp_list"].append({"aln":[]})
                hsp_idx += 1
                aln_idx = -1
                score = " ".join(line.strip().split(" ")[2:5]).replace(",","")
                evalue = line.strip().split(" ")[8].replace(",","")
                method = line.strip().split("Method: ")[1]
                res_obj_dict[sbj_id]["hsp_list"][hsp_idx]["score"] = score
                res_obj_dict[sbj_id]["hsp_list"][hsp_idx]["evalue"] = evalue
                res_obj_dict[sbj_id]["hsp_list"][hsp_idx]["method"] = method
            elif line.find("Identities = ") != -1:
                identities = line.strip().split(" ")[2] 
                identities += " " + line.strip().split(" ")[3].replace(",","")
                positives = line.strip().split(" ")[6]
                positives += " " + line.strip().split(" ")[7].replace(",","")
                gaps = line.strip().split(" ")[10]
                gaps += " " + line.strip().split(" ")[11].replace(",","")
                res_obj_dict[sbj_id]["hsp_list"][hsp_idx]["identities"] = identities
                res_obj_dict[sbj_id]["hsp_list"][hsp_idx]["positives"] = positives
                res_obj_dict[sbj_id]["hsp_list"][hsp_idx]["gaps"] = gaps
            elif line[0:6] == "Query ":
                res_obj_dict[sbj_id]["hsp_list"][hsp_idx]["aln"].append({})
                aln_idx += 1 
                res_obj_dict[sbj_id]["hsp_list"][hsp_idx]["aln"][aln_idx]["query"] = line
                query_open = True
            elif query_open == True:
                res_obj_dict[sbj_id]["hsp_list"][hsp_idx]["aln"][aln_idx]["matches"] = line
                query_open = False
            elif line[0:6] == "Sbjct ":
                res_obj_dict[sbj_id]["hsp_list"][hsp_idx]["aln"][aln_idx]["sbjct"] = line


    canon_list = res_obj_dict.keys()

    sec_list = ["ptm_annotation", "glycation", "snv", "site_annotation", "glycosylation",
        "site_annotation", "glycosylation", "mutagenesis", "phosphorylation"        
    ]
    prj_obj = {"uniprot_canonical_ac":1, "uniprot_id":1, "protein_names":1, "species":1}
    for sec in sec_list:
        prj_obj[sec] = 1

    for canon in canon_list:
        mongo_query = {"uniprot_canonical_ac":{"$eq": canon}}
        doc  = dbh["c_protein"].find_one(mongo_query,prj_obj)
        sp_obj = doc["species"][0]
        o = {"tax_id":sp_obj["taxid"], "name":sp_obj["name"],
                "common_name":sp_obj["common_name"]}
        res_obj_dict[canon]["details"] = {}
        res_obj_dict[canon]["details"]["species"] = o
        res_obj_dict[canon]["details"]["protein_name"] = doc["protein_names"][0]["name"]
        res_obj_dict[canon]["details"]["uniprot_id"] = doc["uniprot_id"]
        for o in doc["protein_names"]:
            if o["type"] == "recommended":
                res_obj_dict[canon]["details"]["protein_name"] = o["name"]
                break
        for sec in sec_list:
            res_obj_dict[canon]["details"][sec] = doc[sec]


    for sbj_id in res_obj_dict:
        sbj_name = res_obj_dict[sbj_id]["details"]["protein_name"]
        sbj_uniprot_id = res_obj_dict[sbj_id]["details"]["uniprot_id"]
        sbj_tax_id = res_obj_dict[sbj_id]["details"]["species"]["tax_id"]
        sbj_tax_name = res_obj_dict[sbj_id]["details"]["species"]["name"]
        #res_obj_dict[sbj_id].pop("protein_name")
        #res_obj_dict[sbj_id].pop("species")
        #res_obj_dict[sbj_id].pop("uniprot_id")
        for obj in res_obj_dict[sbj_id]["hsp_list"]:
            qry, sbj, matches = "", "", ""
            q_ranges, s_ranges = [], []
            for o in obj["aln"]:
                #qry += o["query"][12:].split(" ")[0]
                #sbj += o["sbjct"][12:].split(" ")[0]
                q_parts, s_parts = o["query"].strip().split(), o["sbjct"].strip().split()
                qry += q_parts[2]
                sbj += s_parts[2]
                aln_offset = o["query"].find(q_parts[2])
                matches += o["matches"][aln_offset:].replace("\n","")
                q_ranges.append({"s":int(q_parts[1]), "e":int(q_parts[3])})
                s_ranges.append({"s":int(s_parts[1]), "e":int(s_parts[3])})
            
            obj["sequences"] = []
            start_pos, end_pos = q_ranges[0]["s"], q_ranges[-1]["e"]
            o = {"aln":qry, "name":"Submitted query sequence", 
                    "id":query_id, "uniprot_ac":"","uniprot_id": "", 
                    "tax_name": "", "tax_id":0, "start_pos":start_pos, "end_pos":end_pos}
            obj["sequences"].append(o)

            start_pos, end_pos = s_ranges[0]["s"], s_ranges[-1]["e"]
            o = {"aln":sbj, "name":sbj_id,
                    "id":sbj_id, "uniprot_ac":sbj_id,"uniprot_id": sbj_uniprot_id, 
                    "tax_name": sbj_tax_name, "tax_id":sbj_tax_id,
                    "start_pos":start_pos, "end_pos":end_pos}
            obj["sequences"].append(o)

            o = {"aln":matches, "name":"Matching residues",
                    "id":"matches", "uniprot_ac":"","uniprot_id": "",
                    "tax_name": "", "tax_id":0, }
            obj["sequences"].append(o)

            obj.pop("aln")
     
    res_obj = {"by_subject":res_obj_dict, "raw":raw}

    return res_obj





def job_status(query_obj, config_obj):

    dbh, error_obj = get_mongodb()
    if error_obj != {}:
        return error_obj


    res_obj = {}
    try:
        q_obj = {"jobid":query_obj["jobid"]}
        job_doc = dbh["c_job"].find_one(q_obj)
        if job_doc == None:
            return {"error_list":[{"error_code":"job-record-not-found"}]}
        #update job status
        status_obj = update_job_status(dbh, job_doc, config_obj)
        if "error_list" in status_obj:
            return status_obj
        res_obj = status_obj
        if res_obj["status"] == "finished":
            res_obj["output_files"] = []
            idx = 0
            for f_obj in config_obj["jobinfo"][job_doc["jobtype"]]["output_files"]:
                url = "https://data.glygen.org"
                if config_obj["server"] in ["dev", "tst"]:
                    url = "https://data.%s.glygen.org" % (config_obj["server"])
                elif config_obj["server"] in ["beta"]:
                    url = "https://beta-data.glygen.org"
                url += "/ln2data/userdata/%s/jobs/%s/%s" % (config_obj["server"], job_doc["jobid"], f_obj["name"])
                o = {"format":f_obj["format"], "url":url}
                res_obj["output_files"].append(o)
                if idx == 0:
                    in_dir = config_obj[config_obj["server"]]["pathinfo"]["userdata"]
                    in_dir += str(job_doc["jobid"])
                    out_file = in_dir + "/" + f_obj["name"] 
                    if os.path.isfile(out_file) == False:
                        err = "invalid-file jobid=%s, filename=%s" % (job_doc["jobid"],f_obj["name"])
                        return {"error_list":[{"error_code":err}]}
                    res_obj["result_count"] = get_result_count(job_doc["jobtype"], out_file)
                idx += 1
    except Exception as e:
        res_obj = {"error_list":[{"error_code":str(e)}]}

    return res_obj
  



def get_result_count(job_type, out_file):

    n = 0
    if job_type in ["structure_search"]:
        doc = json.loads(open(out_file, "r").read())
        if "result" in doc:
            n = len(doc["result"])
    elif job_type == "blastp":
        cmd = "grep \"Score =\" %s | wc" % (out_file)
        n = int(subprocess.getoutput(cmd).strip().split(" ")[0])

    return n


 
def job_detail(query_obj, config_obj):
    dbh, error_obj = get_mongodb()
    if error_obj != {}:
        return error_obj


    res_obj = {}
    try:
        q_obj = {"jobid":query_obj["jobid"]}
        res_obj = dbh["c_job"].find_one(q_obj)
        if res_obj == None:
            return {"error_list":[{"error_code":"record-not-found"}]}
       
        #update job status
        status_obj = update_job_status(dbh, res_obj, config_obj)
        if "error_list" in status_obj:
            return status_obj
        res_obj["status"] = status_obj

        res_obj["id"] = str(res_obj["_id"])
        res_obj.pop("_id")
        for k in ["createdts", "updatedts"]:
            if k not in res_obj:
                continue
            res_obj[k] = res_obj[k].strftime('%Y-%m-%d %H:%M:%S %Z%z')
    except Exception as e:
        res_obj = {"error_list":[{"error_code":str(e)}]}

    return res_obj


def job_list(query_obj, config_obj):

    dbh, error_obj = get_mongodb()
    if error_obj != {}:
        return error_obj

    #Collect errors 
    error_list = get_errors_in_query("job_list",query_obj, config_obj)
    if error_list != []:
        return {"error_list":error_list}


    import pymongo
    res_obj = []
    try:
        doc_list = dbh["c_job"].find({}).sort('createdts', pymongo.DESCENDING)
        for doc in doc_list:
            doc["id"] = str(doc["_id"])
            doc.pop("_id")
            for k in ["createdts", "updatedts"]:
                if k not in doc:
                    continue
                doc[k] = doc[k].strftime('%Y-%m-%d %H:%M:%S %Z%z')
            res_obj.append(doc)
    except Exception as e:
        res_obj = {"error_list":[{"error_code":str(e)}]}


    return res_obj


def job_update(query_obj, config_obj):

    dbh, error_obj = get_mongodb()
    if error_obj != {}:
        return error_obj


    #Collect errors 
    error_list = get_errors_in_query("job_update",query_obj, config_obj)
    if error_list != []:
        return {"error_list":error_list}

    res_obj = {}
    try: 
        q_obj = {"_id":ObjectId(query_obj["id"])}
        update_obj = {}
        for k in query_obj:
            if k not in ["token", "id"]:
                update_obj[k] = query_obj[k]
        res = dbh["c_job"].update_one(q_obj, {'$set':update_obj}, upsert=True)
        res_obj = {"type":"success"}
    except Exception as e:
        res_obj = {"error_list":[{"error_code":str(e)}]}


    return res_obj



def job_delete(query_obj, config_obj):

    dbh, error_obj = get_mongodb()
    if error_obj != {}:
        return error_obj

    #Collect errors 
    error_list = get_errors_in_query("job_delete",query_obj, config_obj)
    if error_list != []:
        return {"error_list":error_list}

    res_obj = {}
    try:
        q_obj = {"_id":ObjectId(query_obj["id"])}
        doc = dbh["c_job"].find_one(q_obj)
        if doc == None:
            res_obj =  {"error_list":[{"error_code":"record-not-found"}]}
        else:
            update_obj = {"visibility":"hidden"}
            res = dbh["c_job"].update_one(q_obj, {'$set':update_obj}, upsert=True)
            res_obj = {"type":"success"}
    except Exception as e:
        res_obj = {"error_list":[{"error_code":str(e)}]}

    return res_obj


def job_clean(data_path, server):

    dbh, error_obj = get_mongodb()
    if error_obj != {}:
        return error_obj

    res_obj = {}
    try:
        res = dbh["c_job"].delete_many({})
        res_obj = {"type":"success"}
        in_dir = data_path + "/userdata/" + server + "/jobs/*"
        cmd = "rm -rf " + in_dir
        x = subprocess.getoutput(cmd)
        #res_obj["cmd"] = x
    except Exception as e:
        res_obj = {"error_list":[{"error_code":str(e)}]}

    return res_obj

def validate_protein_seq(seq):

    seq = seq.upper()
    e_list = []
    aa_string = "ABCDEFGHIJKLMNOPQRSTUVWXYZ*-"
    for i in range(len(aa_string)):
        aa = aa_string[i]
        seq = seq.replace(aa, "")
    if seq.strip() != "":
        e_list.append({"error_code": "bad characters in protein sequence"})
    return e_list



def validate_input(query_obj, config_obj, release_dir, server):
    cmd_parts = []
    error_list = []
    if query_obj["jobtype"] not in config_obj["jobinfo"]:
        error_list.append({"error_code": "unknown job type"})
    elif "paramlist" not in config_obj["jobinfo"][query_obj["jobtype"]]:
        error_list.append({"error_code": "no paramters defined for job type"})
    else:
        for obj in config_obj["jobinfo"][query_obj["jobtype"]]["paramlist"]:
            if obj["id"] not in query_obj["parameters"]:
                error_list.append({"error_code": "missing paramter = %s" % (obj["id"])})
            else:
                val_type = str(type(query_obj["parameters"][obj["id"]])).split(" ")[-1].replace(">","")
                val_type = val_type.replace("'","")
                if obj["type"] == "float" and val_type == "int":
                    query_obj["parameters"][obj["id"]] = float(query_obj["parameters"][obj["id"]])
                    val_type = "float"
                if obj["type"] != val_type:
                    error_list.append({"error_code": "bad value type for paramter=%s" % (obj["id"])})
                elif "cmdflag" in obj:
                    val = query_obj["parameters"][obj["id"]]
                    cmd_parts.append({"flag":obj["cmdflag"], "value":val, "field":obj["id"]})

        
    query_obj["cmd"] = "%s" % (config_obj["jobinfo"][query_obj["jobtype"]]["path"][server])


    for o in cmd_parts:
        if query_obj["jobtype"] == "blastp":
            if o["flag"] == "-db":
                o["value"] = release_dir + "blastdb/" + o["value"]
        query_obj["cmd"] += " %s %s" % (o["flag"], o["value"])

    query_obj["seq_id"] = "QUERY"
    res_obj = {"buffer":""}
    if query_obj["jobtype"] == "blastp":
        e_list = validate_protein_seq(query_obj["parameters"]["seq"])
        if e_list != []:
            return res_obj, e_list
        res_obj["buffer"] = ">%s\n%s\n" % (query_obj["seq_id"], query_obj["parameters"]["seq"])
        
        #cmd = "echo %s %s | /usr/bin/md5sum" % (query_obj["seq_id"], query_obj["parameters"]["seq"])
        #query_obj["md5sum"] = subprocess.getoutput(cmd).split(" ")[0]
        hash_str = "%s %s" % (query_obj["seq_id"], query_obj["parameters"]["seq"])
        hash_obj = hashlib.md5(hash_str.encode('utf-8'))
        query_obj["md5sum"] = hash_obj.hexdigest()
    elif query_obj["jobtype"] in ["structure_search"]:
        res_obj["buffer"] = json.dumps(query_obj["parameters"])
        #cmd = "echo \"%s\" | /usr/bin/md5sum" % (query_obj["parameters"]["seq"])
        #query_obj["md5sum"] = subprocess.getoutput(cmd).split(" ")[0]
        hash_str = "%s %s" % (query_obj["seq_id"], query_obj["parameters"]["seq"])
        hash_obj = hashlib.md5(hash_str.encode('utf-8'))
        query_obj["md5sum"] = hash_obj.hexdigest()

    return res_obj, error_list




def get_job_status(ts_id, config_obj):

    obj = {"tsid":ts_id}
    cmd = "%s -s %s" % (config_obj["jobinfo"]["tspath"], ts_id)
    obj["status"] = subprocess.getoutput(cmd).split(" ")[0]
    cmd = "%s -i %s" % (config_obj["jobinfo"]["tspath"], ts_id)
    for line in subprocess.getoutput(cmd).split("\n"):
        k = line.split(":")[0].replace(" ", "_").lower()
        obj[k] = ":".join(line.split(":")[1:])
        obj[k] = obj[k].strip()
        

    if obj["status"] == "finished" and obj["exit_status"] != "died with exit code 0":
        obj["status"] = "died"
        obj.pop("exit_status")
        cmd = "%s -t %s" % (config_obj["jobinfo"]["tspath"], ts_id)
        obj["error"] = subprocess.getoutput(cmd)

    return obj


def update_job_status(dbh, job_doc, config_obj):

    #If job is finished, don't do anything
    if "status" in job_doc:
        if job_doc["status"]["status"] == "finished":
            f_obj = config_obj["jobinfo"][job_doc["jobtype"]]["output_files"][0]
            in_dir = config_obj[config_obj["server"]]["pathinfo"]["userdata"]
            in_dir += str(job_doc["jobid"])
            out_file = in_dir + "/" + f_obj["name"]
            job_doc["status"]["result_count"] = get_result_count(job_doc["jobtype"], out_file)
            return job_doc["status"]

    res_obj = {}
    try:
        res_obj = get_job_status(job_doc["tsid"], config_obj)
        q_obj = {"jobid":job_doc["jobid"]}
        update_obj = {"status":res_obj}
        res = dbh["c_job"].update_one(q_obj, {'$set':update_obj}, upsert=True)
    except Exception as e:
        res_obj = {"error_list":[{"error_code":str(e)}]}

    return res_obj


