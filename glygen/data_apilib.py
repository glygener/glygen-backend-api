import os
import string
import random
import hashlib
import json
import datetime,time
import pytz
from collections import OrderedDict
from flask import Flask, request, jsonify, Response, stream_with_context
import zlib
import gzip
import struct           
import subprocess

from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord

from glygen.db import get_mongodb
from glygen.util import cache_record_list,  extract_name, get_errors_in_query, order_obj, order_list, get_cached_motif_records_direct, get_cached_records_direct, get_cached_records_indirect
from glygen.motif_apilib import get_parent_glycans




def list_download(query_obj, config_obj, data_path):

    dbh, error_obj = get_mongodb()
    if error_obj != {}:
        return error_obj

    init_obj = dbh["c_init"].find_one({})
    img_path = data_path + "/releases/data/v-%s/glycanimages_snfg/" % (init_obj["dataversion"])

    #Collect errors 
    error_list = get_errors_in_query("list_download",query_obj, config_obj)
    if error_list != []:
        if error_list[0]["field"] != "id" and query_obj["download_type"] != "motif_list":
            return {"error_list":error_list}

    if query_obj["download_type"] not in config_obj["downloadtypes"].keys():
        error_list.append({"error_code":"download-type-not-supported"})
        return {"error_list":error_list}
    
    if query_obj["format"].lower() not in config_obj["downloadtypes"][query_obj["download_type"]]["formatlist"]:
        error_list.append({"error_code":"download-type-format-combination-not-supported"})
        return {"error_list":error_list}

    if query_obj["format"].lower() not in config_obj["mimetypes"]:
        error_list.append({"error_code":"non-existent-mime-type-for-submitted-format"})
        return {"error_list":error_list}

    format_lc = query_obj["format"].lower()
    download_type_list = [
        "glycan_list", "site_list", "motif_list","protein_list", "genelocus_list", "ortholog_list",
        "idmapping_list_mapped", "idmapping_list_unmapped", "idmapping_list_all", 
        "idmapping_list_all_collapsed"
    ]
    sequence_format_list = ["fasta", "iupac", "wurcs","glycam","smiles_isomeric","inchi","glycoct", "byonic", "grits"]

    data_buffer = ""
    if query_obj["download_type"] in download_type_list:
        list_obj = get_list_object(query_obj, config_obj)
        if "error_list" in list_obj:
            return list_obj
        if format_lc in ["json"]:
            data_buffer = json.dumps(list_obj["results"], indent=4)
        elif format_lc in ["csv", "tsv"]:
            data_buffer = get_tabular_buffer(list_obj, query_obj, config_obj)
        elif format_lc in sequence_format_list:
            data_buffer = get_sequence_buffer_one(dbh, list_obj, query_obj, config_obj)

    #Now that we have data_buffer, let's worry about compression
    if query_obj["compressed"] == True:
        fname = "%s.%s" % (query_obj["id"], query_obj["format"])
        c_data_buffer = gzip.compress(bytes(data_buffer, 'utf-8'))
        res_stream = Response(c_data_buffer, mimetype='application/gzip')
        res_stream.headers['Content-Disposition'] = 'attachment; filename=%s.gz' % (fname)
    else:
        res_stream = Response(data_buffer, mimetype=config_obj["mimetypes"][format_lc])
    return res_stream





def detail_download(query_obj, config_obj, data_path):


    dbh, error_obj = get_mongodb()
    if error_obj != {}:
        return error_obj

    init_obj = dbh["c_init"].find_one({})
    img_path = data_path + "/releases/data/v-%s/glycanimages_snfg/" % (init_obj["dataversion"])

    #Collect errors 
    error_list = get_errors_in_query("detail_download",query_obj, config_obj)
    if error_list != []:
        if error_list[0]["field"] != "id" and query_obj["download_type"] != "motif_list":
            return {"error_list":error_list}

    if query_obj["download_type"] not in config_obj["downloadtypes"].keys():
        error_list.append({"error_code":"download-type-not-supported"})
        return {"error_list":error_list}
    
    if query_obj["format"].lower() not in config_obj["downloadtypes"][query_obj["download_type"]]["formatlist"]:
        error_list.append({"error_code":"download-type-format-combination-not-supported"})
        return {"error_list":error_list}

    if query_obj["format"].lower() not in config_obj["mimetypes"]:
        error_list.append({"error_code":"non-existent-mime-type-for-submitted-format"})
        return {"error_list":error_list}

    img_file = img_path +  "G0000000.png"
    format_lc = query_obj["format"].lower()
    
    download_type_list =  [
        "glycan_detail", "motif_detail", "protein_detail","protein_detail_isoformset","protein_detail_homologset", 
        "site_detail", "publication_detail", "glycan_image", "biomarker_detail"
    ]
    sequence_format_list = ["fasta", "iupac", "wurcs","glycam","smiles_isomeric","inchi","glycoct", "byonic", "grits"]

    data_buffer = ""
    if query_obj["download_type"] in download_type_list:
        record_obj = get_record_object(dbh, query_obj, config_obj)
        
        if record_obj == None:
            return {"error_list":{"error_code":"non-existent-record"}}
        elif query_obj["download_type"] in ["glycan_image"] and format_lc in ["png"]:
            img_file = img_path + query_obj["id"].upper() + ".png"
            if os.path.isfile(img_file) == False:
                img_file = img_path +  "G0000000.png"
            data_buffer = open(img_file, "rb").read()
        elif query_obj["download_type"] in ["motif_detail"] and format_lc in ["csv", "tsv"]:
            m_query = {"motifs.id": {'$eq': query_obj["id"]}}
            row = ["glytoucan_ac"]
            if format_lc == "csv":
                data_buffer += "\"" +  "\",\"".join(row) + "\"\n"
            elif format_lc == "tsv":
                data_buffer += "\"" +  "\"\t\"".join(row) + "\"\n"
            for o in dbh["c_glycan"].find(m_query):
                row = [o["glytoucan_ac"]]
                data_buffer += "\"" +  "\",\"".join(row) + "\"\n"
        elif query_obj["download_type"] in ["motif_detail"] and format_lc in ["png"]:
            data_buffer = ""
            glytoucan_ac = record_obj["glytoucan_ac"]
            img_file = img_path + glytoucan_ac.upper() + ".png"
            if os.path.isfile(img_file) == False:
                img_file = img_path +  "G0000000.png"
            data_buffer = open(img_file, "rb").read()
        elif format_lc in sequence_format_list:
            data_buffer = get_sequence_buffer_two(dbh, record_obj, query_obj)
        else:
            data_buffer = json.dumps(record_obj,  indent=4)


    #Now that we have data_buffer, let's worry about compression
    if query_obj["compressed"] == True:
        fname = "%s.%s" % (query_obj["id"], query_obj["format"])
        c_data_buffer = gzip.compress(bytes(data_buffer, 'utf-8'))
        res_stream = Response(c_data_buffer, mimetype='application/gzip')
        res_stream.headers['Content-Disposition'] = 'attachment; filename=%s.gz' % (fname)
    else:
        res_stream = Response(data_buffer, mimetype=config_obj["mimetypes"][format_lc])
    #print data_buffer

    return res_stream





def section_download(query_obj, config_obj, sec_info, data_path):

    
    dbh, error_obj = get_mongodb()
    if error_obj != {}:
        return error_obj

    #Collect errors 
    error_list = get_errors_in_query("section_download",query_obj, config_obj)
    if error_list != []:
        return {"error_list":error_list}

    if query_obj["download_type"] not in config_obj["downloadtypes"].keys():
        error_list.append({"error_code":"download-type-not-supported"})
        return {"error_list":error_list}
    
    if query_obj["format"].lower() not in config_obj["downloadtypes"][query_obj["download_type"]]["formatlist"]:
        error_list.append({"error_code":"download-type-format-combination-not-supported"})
        return {"error_list":error_list}

    if query_obj["format"].lower() not in config_obj["mimetypes"]:
        error_list.append({"error_code":"non-existent-mime-type-for-submitted-format"})
        return {"error_list":error_list}
   
    format_lc = query_obj["format"].lower()
    download_type_list =  [ "protein_section", "site_section", "glycan_section", 
        "motif_section", "publication_section", "biomarker_section"]


    data_buffer = ""
    if query_obj["download_type"] in download_type_list:
        record_obj = get_record_object(dbh, query_obj, config_obj)
        if record_obj == None:
            return {"error_list":{"error_code":"non-existent-record"}}
        if "section" not in query_obj:
            return {"error_list":{"error_code":"missing-required-field (section)"}}
        
        sec = query_obj["section"]
        record_type = query_obj["download_type"].split("_")[0] 
        if record_type not in sec_info:
            return {"error_list":{"error_code":"unknown-record-type"}}
        if sec not in sec_info[record_type]:
            return {"error_list":{"error_code":"unknown-section"}}

        if "sectionfield" not in sec_info[record_type][sec]:
            return {"error_list":{"error_code":"unknown-section-field"}}

        sec_field = sec_info[record_type][sec]["sectionfield"]
        if sec_field not in record_obj:
            return {"error_list":{"error_code":"missing-section-field"}}
       
        filter_info = sec_info[record_type][sec]["filterinfo"]
        filter_type = filter_info["filtertype"] if "filtertype" in filter_info else ""

        lbl_dict = {}
        for o in sec_info[record_type][sec]["fieldmap"]:
            lbl_dict[o["path"]] = o["label"]
        

        list_obj = {"results":[]}
        obj_list = record_obj[sec_field]
        if record_type == "biomarker" and query_obj["section"] == "component_glycan":
            obj_list = record_obj[sec_field]["glycan"]
        elif record_type == "biomarker" and query_obj["section"] == "component_protein":
            obj_list = record_obj[sec_field]["protein"] 

        for obj in obj_list:
            if filter_info["field"] != "":
                if filter_info["field"] in obj:
                    field_val = obj[filter_info["field"]]
                    if type(field_val) is str:
                        if filter_type == "exclude" and field_val in filter_info["valuelist"]:
                            continue
                        elif field_val not in filter_info["valuelist"]:
                            continue
                    elif type(field_val) is list:
                        overlap = False
                        for v in filter_info["valuelist"]:
                            if v in field_val:
                                overlap = True
                        if filter_type == "exclude" and overlap == True:
                            continue
                        elif filter_type != "exclude" and overlap == False:
                            continue

            #return lbl_dict

            o = {}
            for path in lbl_dict:
                p_list = path.split(".")
                val_obj = obj
                for p in p_list:
                    val_obj = val_obj[p] if p in val_obj else val_obj
           
                if sec.find("snv_") != -1 and path == "sequence":
                    val_obj = "%s -> %s" % (obj["sequence_org"], obj["sequence_mut"])

                # get deeper into structure for "disease" obj list 
                if type(val_obj) is list and path == "disease":
                    tmp_list = []
                    for oo in obj[path]:
                        if "recommended_name" in oo:
                            d = "%s (%s)" % (oo["recommended_name"]["name"], oo["recommended_name"]["id"])
                            tmp_list.append(d)
                    val_obj = "; ".join(tmp_list)

                if type(val_obj) in [str, int, float]:
                    lbl = lbl_dict[path] if path in lbl_dict else path
                    o[lbl] = str(val_obj)
                
                    


            if "evidence" in obj:
                if obj["evidence"] != []:
                    for oo in obj["evidence"]:
                        #new_o = o
                        new_o = {}
                        for k in o:
                            new_o[k] = o[k]
                        xref_db = oo["database"] if "database" in oo else ""
                        xref_url = oo["url"] if "url" in oo else ""
                        xref_id = oo["id"] if "id" in oo else ""
                        new_o["Source Xref DB"] = xref_db
                        new_o["Source Xref ID"] = xref_id 
                        new_o["Source Xref URL"] = xref_url
                        list_obj["results"].append(new_o)
                else:
                    list_obj["results"].append(o)
            else:
                list_obj["results"].append(o)



        if format_lc in ["csv", "tsv"]:
            data_buffer = get_tabular_buffer(list_obj, query_obj, config_obj)


    #t_list = []
    #seen = {}
    #for o in list_obj["results"]:
    #    if o["GlyTouCan Accession"] == "G83461WR" and o["Start Position"] == "128":
    #        s = json.dumps(o)
    #        if s not in seen:
    #            t_list.append(o)
    #            seen[s] = True
    #return t_list

    
    #Now that we have data_buffer, let's worry about compression
    if query_obj["compressed"] == True:
        fname = "%s.%s" % (query_obj["id"], query_obj["format"])
        c_data_buffer = gzip.compress(bytes(data_buffer, 'utf-8'))
        res_stream = Response(c_data_buffer, mimetype='application/gzip')
        res_stream.headers['Content-Disposition'] = 'attachment; filename=%s.gz' % (fname)
    else:
        res_stream = Response(data_buffer, mimetype=config_obj["mimetypes"][format_lc])

    #print data_buffer

    return res_stream










def get_fasta_sequence(dbh, canon, isoform_ac, seq_type):

    mongo_query = {"uniprot_canonical_ac":canon}
    doc = dbh["c_protein"].find_one(mongo_query)

    sec_doc = doc["sequence"]
    if seq_type == "isoform":
        for o in doc["isoforms"]:
            if isoform_ac == o["isoform_ac"]:
                sec_doc = o["sequence"]
                break
    seq_str = sec_doc["sequence"]
    seq_header = sec_doc["header"]
    seq_obj = SeqRecord(Seq(seq_str),id="x",description="xxx")
    seq_lines = seq_obj.format("fasta").split("\n")
    seq_lines = [">"+seq_header] + seq_lines[1:]
    seq = "\n".join(seq_lines) + "\n"

    return seq




def get_tabular_buffer(list_obj, query_obj, config_obj):

    data_buffer = ""
    ordr_dict = {}
    format_lc = query_obj["format"].lower() 
    type_list_one = [
        "idmapping_list_mapped", "idmapping_list_unmapped", "idmapping_list_all", "idmapping_list_all_collapsed"
    ]
    format_list_one = ["iupac", "wurcs","glycam","smiles_isomeric","inchi","glycoct", "byonic", "grits"]
    format_list_two = ["fasta"]

    if query_obj["download_type"] in config_obj["objectorder"]:
        ordr_dict = config_obj["objectorder"][query_obj["download_type"]]
                                                                    
    if query_obj["download_type"] in type_list_one:
        new_list_obj = []
        mapped_legends = list_obj["cache_info"]["mapped_legends"]
        unmapped_legends = list_obj["cache_info"]["unmapped_legends"]
        legend_dict = mapped_legends
        if query_obj["download_type"] == "idmapping_list_unmapped":
            legend_dict = unmapped_legends
        #print json.dumps(list_obj["results"], indent=4)
        for j in range(0, len(list_obj["results"])):
            obj = list_obj["results"][j]
            if query_obj["download_type"] == "idmapping_list_mapped":
                if obj["category"] == "unmapped":
                    continue
            if query_obj["download_type"] == "idmapping_list_unmapped":
                if obj["category"] == "mapped":
                    continue
                    
            if query_obj["download_type"] in ["idmapping_list_all", "idmapping_list_all_collapsed"]:
                legend_dict["input_id"] = legend_dict["from"]
                legend_dict["reason"] = legend_dict["to"]

            new_obj = {}
            for k in obj:
                if k in ["category", "hit_score"]:
                    continue
                new_obj[legend_dict[k]] = obj[k]
                if k in ordr_dict:
                    ordr_dict[legend_dict[k]] = ordr_dict[k]
            new_list_obj.append(new_obj)
                                
        if query_obj["download_type"] == "idmapping_list_all_collapsed":
            collapse_dict = {}
            list_obj["results"] = []
            for obj in new_list_obj:
                in_id = obj[legend_dict["from"]]
                anchor = obj[legend_dict["anchor"]] if legend_dict["anchor"] in obj else ""
                out_id = obj[legend_dict["to"]]                      
                if in_id not in collapse_dict:
                    collapse_dict[in_id] = {"to":[], "anchor":[]}
                if anchor not in collapse_dict[in_id]["anchor"]:
                    collapse_dict[in_id]["anchor"].append(anchor)
                if out_id not in collapse_dict[in_id]["to"]:
                    collapse_dict[in_id]["to"].append(str(out_id))

            for in_id in collapse_dict:
                out_id = ",".join(collapse_dict[in_id]["to"])
                anchor = ",".join(collapse_dict[in_id]["anchor"])
                obj = {legend_dict["from"]:in_id, legend_dict["to"]:out_id, 
                        legend_dict["anchor"]:anchor}
                list_obj["results"].append(obj)
        else:
            list_obj["results"] = new_list_obj

    if len(list_obj["results"]) > 0:
        key_list = order_list(list_obj["results"][0].keys(), ordr_dict)
        if "GlyTouCan Accession" in key_list:
            key_list.append("Glycan Image Url")
        if format_lc == "csv":
            data_buffer = "\"" +  "\",\"".join(key_list) + "\"\n"
        else:
            data_buffer = "\"" +  "\"\t\"".join(key_list) + "\"\n"

        seen_row = {}
        line_list = []
        for j in range(0, len(list_obj["results"])):
            obj = list_obj["results"][j]
            row = []
            for k in key_list:
                val_k = str(obj[k]) if k in obj else ""
                if query_obj["download_type"] == "ortholog_list" and k == "sequence":
                    val_k = obj[k]["sequence"]
                if query_obj["download_type"] == "ortholog_list" and k == "evidence":
                    val_k = obj[k][0]["url"]
                #if query_obj["download_type"] == "site_list" and k in ["glycosylation", "mutagenesis", "snv","site_annotation"]:
                #val_k = "yes" if len(obj[k]) > 0 else "no"
                row.append(val_k)
            if "GlyTouCan Accession" in key_list:
                glytoucan_ac = obj["GlyTouCan Accession"]
                image_url = "https://api.glygen.org/glycan/image/%s" % (glytoucan_ac)
                row.append(image_url)
            s = json.dumps(row)
            if s in seen_row:
                continue
            seen_row[s] = True
            line = "\"" +  "\"\t\"".join(row) + "\"\n"
            if format_lc == "csv":
                line = "\"" +  "\",\"".join(row) + "\"\n"
            line_list.append(line)
        data_buffer += "".join(line_list)
 
    return data_buffer


def get_sequence_buffer_one(dbh, list_obj, query_obj, config_obj):

    data_buffer = ""

    format_list_one = ["iupac", "wurcs","glycam","smiles_isomeric","inchi","glycoct", "byonic", "grits"]
    format_list_two = ["fasta"]

    format_lc = query_obj["format"].lower()
    if format_lc in format_list_one:
        res_count = len(list_obj["results"])
        seen_byonic = {}
        seq_lines = []
        for j in range(0, res_count):
            obj = list_obj["results"][j]
            if format_lc not in obj:
                continue
            if format_lc == "byonic":
                if obj[format_lc] not in seen_byonic and obj[format_lc].strip() != "":
                    seq_lines.append("%s" % (obj[format_lc]))
                    seen_byonic[obj[format_lc]] = True
            elif format_lc == "grits":
                seq_lines.append("<glycan GWBSequence=\"%s\" id=\"%s\"/>" % (obj["gwb"],obj["glytoucan_ac"]))
            else:
                seq_lines.append("%s,%s" % (obj["glytoucan_ac"], obj[format_lc]))
        if format_lc == "grits":
            seq_lines = [
                "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>",
                "<database description=\"GlyGen\" name=\"GlyGen\" structureCount=\"%s\" version=\"1.0\">" % (res_count)
            ] + seq_lines + ["</database>"]
        data_buffer += "\n".join(seq_lines)
    elif format_lc in format_list_two:
        seq_list = []
        ac_list = []
        for obj in list_obj["results"]:
            ac_list.append(obj["uniprot_canonical_ac"])
        k = 0
        for protein_obj in dbh["c_protein"].find({"uniprot_canonical_ac":{"$in":ac_list}}):
            k += 1
            if "sequence" not in protein_obj:
                continue
            if "sequence" not in protein_obj["sequence"]:
                continue
            desc = extract_name(protein_obj["protein_names"],"recommended","UniProtKB")
            seq_obj = SeqRecord(
                Seq(protein_obj["sequence"]["sequence"]),
                id=protein_obj["uniprot_canonical_ac"],
                description=desc
            )
            seq_list.append(seq_obj.format("fasta") + "\n\n")
        data_buffer += "".join(seq_list)

    return data_buffer


def get_list_object(query_obj, config_obj):

    collection = config_obj["downloadtypes"][query_obj["download_type"]]["cache"]
    mongo_query = {"list_id":query_obj["id"]}
    if query_obj["download_type"] == "motif_list":
        mongo_query = {}
    list_obj = {}
    if query_obj["download_type"] == "motif_list":
        list_query = {"sort":"glycan_count","order":"desc", "limit":10000000}
        list_obj = get_cached_motif_records_direct(list_query, config_obj)
    else:
        list_query = {"id":query_obj["id"], "limit":10000000}
        if "filters" in query_obj:
            list_query["filters"] = query_obj["filters"]
        if query_obj["download_type"] in ["idmapping_list_all", "idmapping_list_all_collapsed",
            "idmapping_list_mapped","idmapping_list_unmapped", "genelocus_list", "ortholog_list"]:
            list_obj = get_cached_records_direct(list_query, config_obj)
        else:
            list_obj = get_cached_records_indirect(list_query, config_obj)


    if "_id" in list_obj:
        list_obj.pop("_id")
    
    
    return list_obj



def get_record_object(dbh, query_obj, config_obj):

    format_lc = query_obj["format"].lower()
    collection = config_obj["downloadtypes"][query_obj["download_type"]]["cache"]
    main_id = "uniprot_canonical_ac" 

    if query_obj["download_type"] in ["glycan_detail", "glycan_image", "glycan_section"]:
        main_id = "glytoucan_ac" 
    if query_obj["download_type"] in ["motif_detail", "motif_section"]:
        main_id = "motif_ac"
    if query_obj["download_type"] in ["site_detail", "site_section"]:
        main_id = "id"
    if query_obj["download_type"] in ["publication_detail", "publication_section"]:
        main_id = "record_id"
    if query_obj["download_type"] in ["biomarker_detail", "biomarker_section"]:
        main_id = "biomarker_id"    
    mongo_query = {main_id:{"$regex":query_obj["id"], "$options":"i"}}
    record_obj = dbh[collection].find_one(mongo_query)
    if record_obj == None:
        return record_obj

    if format_lc in ["json"]:
        record_obj.pop("_id")
        if query_obj["download_type"] == "protein_detail":
            url = config_obj["urltemplate"]["uniprot"] % (record_obj["uniprot_canonical_ac"])
            record_obj["uniprot"] = { "uniprot_canonical_ac":record_obj["uniprot_canonical_ac"],
                "uniprot_id":record_obj["uniprot_id"],"url":url}
            record_obj.pop("uniprot_canonical_ac")
            record_obj.pop("uniprot_id")
        elif query_obj["download_type"] in ["glycan_detail", "motif_detail"]:
            url = config_obj["urltemplate"]["glytoucan"] % (record_obj["glytoucan_ac"])
            record_obj["glytoucan"] = {
                "glytoucan_ac":record_obj["glytoucan_ac"], 
                "glytoucan_url":url
            }
            m_query = {"motifs.id": {'$eq': record_obj["glytoucan_ac"]}}
            doc_list = dbh["c_glycan"].find(m_query)
            record_obj["results"] = get_parent_glycans(record_obj["glytoucan_ac"], doc_list, record_obj)
            record_obj.pop("glytoucan_ac")

    return record_obj


def get_sequence_buffer_two(dbh, record_obj, query_obj):

    data_buffer = ""

    format_lc = query_obj["format"].lower()
    if format_lc in ["iupac", "wurcs","glycam","smiles_isomeric","inchi","glycoct", "byonic"]:
        data_buffer += record_obj[format_lc]
    elif format_lc in ["fasta"]:
        if query_obj["download_type"] in ["protein_detail"]:
            if "sequence" in record_obj:
                if "sequence" in record_obj["sequence"]:
                    id_lbl, desc = "", ""
                    if "header" in record_obj["sequence"]:
                        parts = record_obj["sequence"]["header"].split(" ")
                        id_lbl = parts[0]
                        desc = " ".join(parts[1:])
                    seq_obj = SeqRecord(Seq(record_obj["sequence"]["sequence"]), id=id_lbl, description=desc)
                    data_buffer += seq_obj.format("fasta") + "\n\n"
                    
        elif query_obj["download_type"] in ["protein_detail_isoformset"]:
            seq_id = record_obj["uniprot_canonical_ac"]
            for o in record_obj["isoforms"]:
                isoform_ac = o["isoform_ac"]
                data_buffer += get_fasta_sequence(dbh, seq_id, isoform_ac, "isoform")
        elif query_obj["download_type"] in ["protein_detail_homologset"]:
            seq_id = record_obj["uniprot_canonical_ac"]
            data_buffer += get_fasta_sequence(dbh, seq_id, seq_id, "canonical")
            for o in record_obj["orthologs"]:
                seq_id = o["uniprot_canonical_ac"]
                data_buffer += get_fasta_sequence(dbh, seq_id, seq_id, "canonical")
    

    return data_buffer

