import os,sys
import string
import glob
import json


__version__="1.0"
__status__ = "Dev"



###############################
def main():

    in_file = "glygen/conf/list_init_categories.csv"
    line_list = open(in_file, "r").read().split("\n")
    cat_dict = {}
    for line in line_list[1:-1]:
        cat_id,cat_label,cat_order = line.split(",")
        cat_dict[cat_id] = {"label":cat_label, "order":cat_order, "tooltip": ""}


    in_file = "glygen/conf/list_init_fields.csv"
    line_list = open(in_file, "r").read().split("\n")
    tmp_dict = {}
    for line in line_list[1:-1]:
        record_type,field_id,field_label,field_order,is_default,is_immutable,category_id_list = line.split(",")
        if record_type not in tmp_dict:
            tmp_dict[record_type] = {"columns":[], "categories":[]}
        obj = {
            "id":field_id,
            "property_name":field_id, 
            "label":field_label, 
            "order":int(field_order), 
            "tooltip": "",
            "immutable":is_immutable.strip() == "true",
            "default":is_default.strip() == "true", 
            "categories": []
        }
        for cat_id in category_id_list.split(";"):
            if cat_id in cat_dict:
                o = {"id":cat_id, "order":cat_dict[cat_id]["order"]}
                obj["categories"].append(o)
        tmp_dict[record_type]["columns"].append(obj)
    
    for record_type in tmp_dict:
        seen = {}
        for obj in tmp_dict[record_type]["columns"]:
            for o in obj["categories"]:
                cat_id = o["id"] 
                if cat_id not in seen:
                    lbl, ordr, tooltip = cat_dict[cat_id]["label"], cat_dict[cat_id]["order"], cat_dict[cat_id]["tooltip"]
                    tmp_dict[record_type]["categories"].append({"id":cat_id, "label":lbl, "order":ordr, "tooltip": tooltip})
                    seen[cat_id] = True
    print (json.dumps(tmp_dict, indent=4))



if __name__ == '__main__':
    main()
