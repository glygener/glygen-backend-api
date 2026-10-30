import os
import random
import hashlib
import json
import datetime,time
import pytz








def parse_sent(s,  max_word_count, min_word_count):

    tmp_dict = {}
    if s.strip() == "":
        return
    s = s.lower().replace(",", " ").replace("-", " ").replace(";", " ")
    s = s.replace("(", " ").replace(")", " ").replace("[", " ").replace("]", " ")
    w_list = s.strip().split(" ")

    word_count = len(w_list) + 1
    word_count = max_word_count if word_count > max_word_count else word_count
    for wlen in range(0, word_count + 1):
        if wlen > len(w_list):
            continue
        for i in range(0, len(w_list)):
            l = []
            for ww in w_list[i:i+wlen]:
                ww = ww.strip()
                if ww != "":
                    l.append(ww)
            if len(l) >= min_word_count:
                phrase = " ".join(l)
                if len(phrase) == 1:
                    continue
                tmp_dict[phrase] = True
    phrase_dict = {}
    for phrase in tmp_dict:
        n = len(phrase.split(" "))
        phrase_dict[n] = phrase
    return phrase_dict




def get_result_dict_one(dbh, phrase_dict, selected_sections, quote_flag, record_type, max_p, debug_flag):
 
    debug_list = [] 
    result_dict = {"all":{}}
    prj_obj = {"record_type":1, "record_id":1, "section":1}
    i = 0
    used_phrase_list = []
    hit_count = 0
    for word_count in sorted(phrase_dict, reverse=True):
        i += 1
        #if i > max_p:
        #    break
        if hit_count > 0:
            break
        phrase = phrase_dict[word_count]
        if quote_flag:
            for c in ["\"", "\'"]:
                phrase = phrase.replace(c, "")
        used_phrase_list.append(phrase)
        qry_obj = {"phraselist":{"$eq":phrase}, "record_type":{"$eq":record_type}}
        n1, n2 = 0, 0
        ignored_sec_list = []
        for doc in dbh["c_index"].find(qry_obj, prj_obj):
            hit_count += 1
            n1 += 1
            record_type, record_id, sec = doc["record_type"], doc["record_id"], doc["section"]
            if record_type == "disease":
                record_id = record_id.lower().replace(":",".")
            #if we are doing term_category != "any"
            if selected_sections != [] and sec not in selected_sections:
                ignored_sec_list.append(sec)
                continue
            n2 += 1
            result_dict["all"][record_id] = word_count
            if sec not in result_dict:
                result_dict[sec] = {}
            result_dict[sec][record_id] = word_count
        if result_dict["all"] != {} or quote_flag:
        #if quote_flag:
            break
        ignored_sec_list = list(set(ignored_sec_list))
        debug_list.append({"mongo_query":qry_obj, "n1":n1, "n2":n2, "ignored":ignored_sec_list})
    if debug_flag:
        return debug_list
    return result_dict, used_phrase_list


