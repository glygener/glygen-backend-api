import os
import csv
import json
import glob
import traceback
from flask import current_app
from gsa.db import log_error
from Bio import SeqIO

ac2canon = {}
protein_master_dict = {}
seq_hash = {}
aa_format_dict = {"one":{}, "three":{}, "glytype":{}}



def run_qc(in_file, file_format, res_obj, qc_type, data_version):

    SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
    json_url = os.path.join(SITE_ROOT, "conf/config.json")
    config_obj = json.load(open(json_url))

    if qc_type in ["glyco_site", "glyco_site_unicarbkb"]:
        data_path, ser = current_app.config["DATA_PATH"], current_app.config["SERVER"]
        release_dir = "%s/releases/data/v-%s/" % (data_path, data_version)
        if os.path.isdir(release_dir) == False:
            error_obj =  {"error":"no data found for submitted data version=%s" % (data_version),"status":0}
            return error_obj

    ac2canon = {}
    protein_master_dict = {}
    seq_hash = {}
    aa_format_dict = {"one":{}, "three":{}, "glytype":{}}
    seen_row = {}

    error_obj = {}
    try:
        if file_format in ["csv", "tsv"]:
            f_dict = {"file_name":"string", "row_number":"number", "row_string":"string", "qc_flags":"string"}
            tmp_list = []
            for f in f_dict:
                tmp_list.append({"type":f_dict[f], "label":f})
            res_obj["failedrows"].append(tmp_list)
            
            data_frame = {}
            sep = "," if file_format == "csv" else "\t"
            file_name = in_file.split("/")[-1]
            load_sheet(data_frame, in_file, [], sep)
            f_list = data_frame["fields"]
            tmp_qc_rows = run_basic_header_sanity(file_name, file_format, f_list, seen_row)
            abort_flag = False
            if qc_type in ["glyco_site", "glyco_site_unicarbkb"]:
                load_data_files(data_version)
                tmp_rows = run_glycosite_header_sanity(file_name, file_format, f_list, seen_row, qc_type)
                abort_flag = True if tmp_rows != [] else abort_flag
                tmp_qc_rows += tmp_rows
            if tmp_qc_rows != []:
                qc_flags = []
                for r in tmp_qc_rows:
                    qc_flags.append("%s (%s)" % (r[-1], r[-2]))
                qc_flags = sorted(qc_flags)
                joined_flags = ";".join(qc_flags)
                res_obj["summary"]["fatal_qc_flags"] += 1 if joined_flags.find("file_ignored") != -1 else 0
                #joined_flags = qc_flags
                #res_obj["summary"]["fatal_qc_flags"] += 1 if "file_ignored" in joined_flags else 0

                res_obj["summary"]["total_qc_flags"] += 1
                res_obj["failedrows"].append([file_name, 0, json.dumps(f_list), joined_flags])

            row_idx = 1
            for row in data_frame["data"]:
                tmp_qc_rows = []
                tmp_qc_rows += run_basic_row_sanity(file_name, file_format, f_list, row, row_idx, seen_row)
                if qc_type in ["glyco_site","glyco_site_unicarbkb"] and abort_flag == False:
                    tmp_qc_rows += run_glycosite_row_sanity(file_name, file_format, f_list, 
                            row, row_idx,seen_row, qc_type)
                if tmp_qc_rows != []:
                    qc_flags = []
                    for r in tmp_qc_rows:
                        qc_flags.append("%s (%s)" % (r[-1], r[-2]))
                    qc_flags = sorted(qc_flags)
                    joined_flags = ";".join(qc_flags)
                    res_obj["summary"]["fatal_qc_flags"] += 1 if joined_flags.find("file_ignored") != -1 else 0 
                    #joined_flags = qc_flags
                    #res_obj["summary"]["fatal_qc_flags"] += 1 if "file_ignored" in joined_flags else 0
                    res_obj["summary"]["total_qc_flags"] += 1
                
                    res_obj["failedrows"].append([file_name, row_idx, json.dumps(row), joined_flags])
                row_idx += 1
    except Exception as e:
        error_obj =  log_error(traceback.format_exc())

    return error_obj




def run_basic_header_sanity(file_name, file_format, f_list, seen_row):
    tmp_qc_rows = []
    try:
        row_str = json.dumps(f_list)
    except Exception as e:
        err = "bad characters in header"
        tmp_qc_rows.append([file_name, 0, err, "file_ignored"])
   
    if json.dumps(f_list) in seen_row:
        err = "redundant row"
        tmp_qc_rows.append([file_name, 0, err, "row_ignored"])
    seen_row[json.dumps(f_list)] = True

    return tmp_qc_rows


def run_basic_row_sanity(file_name, file_format, f_list, row, row_idx, seen_row):
    tmp_qc_rows = []
    try:
        row_str = json.dumps(row)
    except Exception as e:
        err = "bad characters in row"
        tmp_qc_rows.append([file_name,row_idx, err, "file_ignored"])

    if len(f_list) != len(row):
        err = "field_count != value_count"
        tmp_qc_rows.append([file_name,row_idx, err, "file_ignored"])
    
    if json.dumps(row) in seen_row:
        err = "redundant row"
        tmp_qc_rows.append([file_name,row_idx, err, "row_ignored"])
    seen_row[json.dumps(row)] = True


    return tmp_qc_rows



def run_glycosite_header_sanity(file_name, file_format, f_list, seen_row, qc_type):

    SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
    json_url = os.path.join(SITE_ROOT, "conf/config.json")
    config_obj = json.load(open(json_url))
    required_fields = config_obj["qcinfo"][qc_type]["requiredfields"]

    tmp_qc_rows = []
    f_list_lc = [f.lower() for f in f_list]
    for f in required_fields:
        if f not in f_list_lc:
            err = "missing-required-field: '%s'" % (f)
            tmp_qc_rows.append([file_name,0, err, "file_ignored"])

    return tmp_qc_rows



def run_glycosite_row_sanity(file_name, file_format, f_list, row, row_idx, seen_row, qc_type):

    tmp_qc_rows = []
    f_list_lc = [f.lower() for f in f_list]
    uniprotkb_ac, position, amino_acid = "", "", ""
    if qc_type == "glyco_sites_unicarbkb":
        uniprotkb_ac = row[f_list_lc.index("protein")].strip()
        position = row[f_list_lc.index("position")].split("^^")[0]
        amino_acid = row[f_list_lc.index("aminoacid")].split("_")[-1]
    else:
        uniprotkb_ac = row[f_list_lc.index("uniprotkb_ac")].strip()
        position = row[f_list_lc.index("start_pos")]
        amino_acid = row[f_list_lc.index("site_seq")]

    if uniprotkb_ac != "":
        if uniprotkb_ac not in ac2canon:
            err = "uniprotkb_ac:'%s' not mapping to GlyGen canonical" % (uniprotkb_ac)
            tmp_qc_rows.append([file_name,row_idx, err, "row_ignored"])
        else:
            canon = ac2canon[uniprotkb_ac]
            if amino_acid.find("|") != -1:
                list_a = amino_acid.split("|")
                list_b = position.split("|")
                amino_acid = "|".join(list_a)
                position = "|".join(list_b)
            elif position.strip() != "" and position.isdigit() == False:
                list_a, list_b = [], []
                for s in position.split(";"):
                    list_b.append(s[1:])
                    list_a.append(s[0])
                amino_acid = "|".join(list_a)
                position = "|".join(list_b)
            aa_three = amino_acid[0].upper() +  amino_acid[1:].lower() if amino_acid != "" else ""
            aa_pos = int(position) if position != "" and position.isdigit() else 0
            flag_dict = {}
            qc_glyco_position(canon, position, amino_acid, seq_hash[canon], flag_dict)
            for err in flag_dict:
                tmp_qc_rows.append([file_name,row_idx, err, "row_ignored"])

    return tmp_qc_rows



def load_data_files(data_version):

    SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
    json_url = os.path.join(SITE_ROOT, "conf/config.json")
    config_obj = json.load(open(json_url))

    data_path, ser = current_app.config["DATA_PATH"], current_app.config["SERVER"]
    release_dir = "%s/releases/data/v-%s/" % (data_path, data_version)
    reviewed_dir = "%s/releases/data/v-%s/reviewed/" % (data_path, data_version)

    file_list = glob.glob(reviewed_dir + "/*_protein_masterlist.csv")
    for in_file in file_list:
        species = in_file.split("/")[-1].split("_")[0]
        data_frame = {}
        load_sheet(data_frame, in_file, [], ",")
        f_list = data_frame["fields"]
        for row in data_frame["data"]:
            canon = row[f_list.index("uniprotkb_canonical_ac")]
            isoform_list = [
                row[f_list.index("reviewed_isoforms")], 
                row[f_list.index("unreviewed_isoforms")]
            ]
            protein_master_dict[canon] = {"species":species}
            for isoform in isoform_list:
                isoform_ac = isoform.split("-")[0].strip()
                canon_ac = canon.split("-")[0].strip()
                if canon_ac == isoform_ac:
                    ac2canon[isoform_ac] = canon


    file_list = glob.glob(reviewed_dir + "/*_protein_allsequences.fasta")
    for fasta_file in file_list:
        for record in SeqIO.parse(fasta_file, "fasta"):
            seq_id = record.id.split("|")[1]
            seq_hash[seq_id] = str(record.seq.upper())

    data_frame = {}
    in_file = release_dir + "/misc/aadict.csv"
    load_sheet(data_frame, in_file, [], ",")
    f_list = data_frame["fields"]
    for row in data_frame["data"]:
        three = row[f_list.index("three")]
        one = row[f_list.index("one")]
        gly_type = row[f_list.index("gly_type")]
        form_list = [one, one.lower(), one.upper(), three, three.lower(), three.upper()]
        for f in form_list:
            aa_format_dict["three"][f] = three
            aa_format_dict["one"][f] = one
            aa_format_dict["glytype"][f] = gly_type

    return 





def load_sheet(sheet_obj, in_file, field_list, separator):

    sheet_obj["fields"] = []
    sheet_obj["data"] = []
    field_ind_list = []
    with open(in_file, 'r') as FR:
        csv_grid = csv.reader(FR, delimiter=separator, quotechar='\"')
        row_count = 0
        ncols = 0
        for row in csv_grid:
            row_count += 1
            if row_count == 1:
                for f in row:
                    sheet_obj["fields"].append(f)
            else:
                new_row = []
                for val in row:
                    new_row.append(val.strip())
                sheet_obj["data"].append(new_row)


    return



def qc_glyco_position(canon, position, amino_acid, canon_seq,  flag_dict):

    aa_three = amino_acid[0].upper() +  amino_acid[1:].lower() if amino_acid != "" else ""
    if position.find("|") != -1:
        pos_list = position.split("|")
        aa_list = amino_acid.split("|")
        if len(pos_list) == len(aa_list):
            for j in xrange(0, len(pos_list)):
                p = pos_list[j]
                a = aa_list[j]
                if p.isdigit() == False:
                    tmp_key = "bad_pos:%s" % (p)
                    flag_dict[tmp_key] = True
                if int(p) == 0 or int(p) >= len(canon_seq):
                    tmp_key = "bad_pos:%s" % (p) 
                    flag_dict[tmp_key] = True
                if a not in aa_format_dict["one"]:
                    tmp_key = "aa_invalid:%s" % (a)
                    flag_dict[tmp_key] = True
                elif aa_format_dict["one"][a] != canon_seq[int(p)-1]:
                    aa_wrong, aa_correct = aa_format_dict["one"][a], canon_seq[int(p)-1] 
                    tmp_key = "aa_mismatch: %s:%s is %s not %s " % (canon, p, aa_wrong,aa_correct)
                    flag_dict[tmp_key] = True
    elif aa_three in aa_format_dict["one"]:
        aa_pos = int(position) if position != "" and position.isdigit() else 0
        if aa_pos == 0 or aa_pos >= len(canon_seq):
            tmp_key = "bad_pos:%s" % (aa_pos)
            flag_dict[tmp_key] = True
        elif aa_format_dict["one"][aa_three] != canon_seq[aa_pos-1]:
            aa_wrong, aa_correct = aa_format_dict["one"][aa_three], canon_seq[aa_pos-1]
            tmp_key = "aa_mismatch: %s:%s is %s not %s " % (canon,aa_pos, aa_wrong,aa_correct)
            flag_dict[tmp_key] = True
    else: #### amino acid is not n or o linked
        tmp_key = "aa_invalid:%s" % (aa_three)
        flag_dict[tmp_key] = True

    return


