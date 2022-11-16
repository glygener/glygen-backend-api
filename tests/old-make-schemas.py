import sys,os
import json
import string
import glob
from genson import SchemaBuilder

def load_properity_lineage(in_obj, parent_key, path):

    if type(in_obj) in [dict]:
        k_list = in_obj.keys()
        for k in k_list:
            new_path = "%s" % (path)
            if parent_key in ["properties"]:
                new_path = "%s.%s" % (path, k) if path != "" else k
                title = meta_dict[new_path]["title"] if new_path in meta_dict else ""
                desc = meta_dict[new_path]["desc"] if new_path in meta_dict else ""
                in_obj[k]["title"] = title
                in_obj[k]["description"] = desc
            if k in ["required"]:
                in_obj[k] = []
            load_properity_lineage(in_obj[k], k, new_path)



    return 


def main():
    
    global meta_dict 

    api_cgi_dir = "/var/www/cgi-bin/api/"
    svc_obj_list = json.loads(open(api_cgi_dir + "conf/validation.conf", "r").read())
    for o in svc_obj_list:
        meta_file = "generated/misc/api_schema.%s.csv" % (o["svc"])
        meta_dict = {}
        if os.path.isfile(meta_file) == True:
            with open(meta_file, "r") as FR:
                for line in FR:
                    parts = line.strip().split(",")
                    path, title, desc = parts[0].strip(),parts[1].strip(),parts[2].strip()
                    meta_dict[path] = {"title":title, "desc":desc}
        
        example_file = o["schemafile"].replace(".schema.", ".example.")
        if os.path.isfile(example_file) == False:
            print "STATUS: failed --> %s not found" % (example_file)
            continue

        example_obj = json.loads(open(example_file,"r").read())
        builder = SchemaBuilder()
        #builder.add_schema({"type": "object", "properties": {}})
        builder.add_object(example_obj)
        #builder.add_object({"fname":"Robel", "lname":"Kahsay", "age":41})
        schema_obj = builder.to_schema()
        #load_properity_lineage(schema_obj, "", "")
        #print json.dumps(schema_obj, indent=4)
        out_file = o["schemafile"]
        with open(out_file, "w") as FW:
            FW.write("%s\n" % (json.dumps(schema_obj, indent=4)))
            print "STATUS: success --> %s generated" % (out_file)




if __name__ == '__main__':
    main()





