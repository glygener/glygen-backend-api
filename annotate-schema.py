import sys,os
import json
import string
from optparse import OptionParser
import glob
import subprocess



def parse_doc(in_obj, path_dict, path):

    if type(in_obj) is dict:
        k_list = list(in_obj.keys())
        for k in k_list:
            p = path + "." + k if path != "" else k
            if k == "type":
                ann_path = path.replace("properties.", "").replace(".items", "")
                if ann_path != "" and path.split(".")[-1] not in ["items", "properties"]:
                    ann = ann_dict[ann_path] if ann_path in ann_dict else "xxxxx: " + ann_path
                    in_obj["description"] = ann
            parse_doc(in_obj[k], path_dict, p)
    elif type(in_obj) is list:
        for k in range(0, len(in_obj)):
            p = path + "." + str(k) if path != "" else str(k)
            if k == "type":
                ann_path = path.replace("properties.", "").replace(".items", "")
                if ann_path != "" and path.split(".")[-1] not in ["items", "properties"]:
                    ann = ann_dict[ann_path] if ann_path in ann_dict else "xxxxx: " + ann_path
                    in_obj["description"] = ann
            parse_doc(in_obj[k], path_dict, p)
    elif type(in_obj) is str:
        path_dict[path] = "*"
    elif type(in_obj) is int:
        path_dict[path] = "0"
    elif type(in_obj) is float:
        path_dict[path] = "0.0"

    return




def main():
   
    usage = "\n%prog  [options]"
    parser = OptionParser(usage,version="%prog version___")
    parser.add_option("-i","--schemafile",action="store",dest="schemafile",help="")
    parser.add_option("-a","--annfile",action="store",dest="annfile",help="")


    (options,args) = parser.parse_args()
    for key in ([options.schemafile, options.annfile]):
        if not (key):
            parser.print_help()
            sys.exit(0)

    schema_file = options.schemafile
    ann_file = options.annfile
   


    global ann_dict


    ann_dict = {}
    #"prop_path","is_required","description"
    line_list = open(ann_file, "r").read().split("\n")
    for line in line_list[1:]:
        line = line.strip().replace("\"", "")
        if line == "":
            continue
        path = line.split(",")[0].replace("*.", "")
        ann_dict[path] = line.split(",")[2].strip()

    schema_obj = json.loads(open(schema_file, "r").read()) 

    path_dict = {}   
    parse_doc(schema_obj, path_dict, "")
    
    #print (json.dumps(path_dict, indent=4))
    #print (json.dumps(schema_obj, indent=4))
    #print (json.dumps(ann_dict, indent=4))
    out_file = schema_file
    with open(out_file, "w") as FW:
        FW.write("%s\n" % (json.dumps(schema_obj, indent=4)))

    return






if __name__ == '__main__':
    main()





