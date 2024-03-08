import os
import string
import json
from flask import Flask, request, jsonify, Response, stream_with_context


from glygen.db import get_mongodb
from glygen.util import cache_record_list,  extract_name, get_errors_in_query, order_obj


    
def getdata (query_obj, config_obj):

    SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
    json_url = os.path.join(SITE_ROOT, "conf/graph.json")
    graph_config_obj = json.load(open(json_url))

    json_url = os.path.join(SITE_ROOT, "conf/ignored_edges.json")
    edge_rules = json.load(open(json_url))
    conn_dict = graph_config_obj["initial"]
    edge_list_all = []
    for src in conn_dict:
        for dst in conn_dict[src]:
            edge = "%s %s" % (src, dst)
            edge_list_all.append(edge)

    edge2idx = {}
    idx2direction = {}
    idx = 1
    for edge in edge_list_all:
        src, dst = edge.split(" ")
        r_edge = "%s %s" % (dst, src)
        if edge not in edge2idx and r_edge not in edge2idx:
            edge2idx[edge] = idx
            idx2direction[idx] = "-->"
            if r_edge in edge_list_all:
                edge2idx[r_edge] = idx
            idx += 1


    concept_list = query_obj["conceptlist"]
    ignore_dict = {}
    for concept in concept_list:
        e_rules = edge_rules[concept]
        ignore_dict[concept] = []
        for o in e_rules:
            edge = "%s %s" % (o["source"],o["target"])
            ignore_dict[concept].append(edge)
            if o["direction"] == "both":
                edge = "%s %s" % (o["target"],o["source"])
                ignore_dict[concept].append(edge)
    
    ignore_list = []
    if concept_list == []:
        ignore_list = edge_list_all
    else:
        i = 0
        concept = concept_list[i]
        ignore_list = set(ignore_dict[concept])
        for i in range(1, len(concept_list)):
            concept = concept_list[i]
            ignore_list = ignore_list.intersection(set(ignore_dict[concept]))
        ignore_list = list(ignore_list)

    n_s_one = {"fill":"#cccccc", "stroke": "3 #cccccc",  "height":30}
    n_s_two = {"fill":"#990000", "stroke": "3 #990000",  "height":30}
    

    res_obj = {"nodes":[], "edges":[]}
    for src in conn_dict:
        s = n_s_two if src in concept_list else n_s_one
        o = {"id":src, "normal":s}
        res_obj["nodes"].append(o)

    e_s_one = {"normal":{"stroke":{"thickness": 2, "color":"#eeeeee", "dash": "3 1"}}}
    e_s_two = {"normal":{
        "stroke":{"thickness": 2, "color":"#990000", "format":"{%id}"}}
    }
    seen_idx = {}
    for edge in edge_list_all:
        src, dst = edge.split(" ")
        r_edge = "%s %s" % (dst, src)
        idx = edge2idx[edge]
        o = {"from":src, "to":dst}
        if edge not in ignore_list and idx not in seen_idx:
            o["normal"] = e_s_two["normal"]
            res_obj["edges"].append(o)
            seen_idx[idx] = True
            if r_edge not in ignore_list:
                o["direction"] = "<-->"


    for edge in edge_list_all:
        src, dst = edge.split(" ")
        idx = edge2idx[edge]
        o = {"from":src, "to":dst}
        if edge in ignore_list and idx not in seen_idx:
            o["normal"] = e_s_one["normal"]
            res_obj["edges"].append(o)
            seen_idx[idx] = True            


    
    return res_obj




