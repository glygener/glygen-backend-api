import os,sys
import string
import glob
import json


__version__="1.0"
__status__ = "Dev"



###############################
def main():

    in_file = "glygen/conf/list_init.csv"
    line_list = open(in_file, "r").read().split("\n")
   
    #print (line_list[0] +",field_label") 
    tmp_dict = {}
    for line in line_list[1:-1]:
        record_type, field_cat, field_name, field_label, cat_order, field_order = line.split(",")
        if record_type not in tmp_dict:
            tmp_dict[record_type] = {}
        if field_cat not in tmp_dict[record_type]:
            obj = {"id":field_cat.lower(), "label":field_cat, "order":int(field_order), "tooltip": "", "options": []}
            tmp_dict[record_type][field_cat] = obj
        o = { "id": field_name, "label":field_label, "order":int(field_order)}
        tmp_dict[record_type][field_cat]["options"].append(o)


    out_dict = {}
    for record_type in tmp_dict:
        out_dict[record_type] = {"columns":[]}
        for field_cat in tmp_dict[record_type]:
            out_dict[record_type]["columns"].append(tmp_dict[record_type][field_cat])

    print (json.dumps(out_dict, indent=4))



if __name__ == '__main__':
    main()
