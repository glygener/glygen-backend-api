import sys,os
import json
import string
import glob
from genson import SchemaBuilder


def is_valid_json(myjson):
    try:
        json_object = json.loads(myjson)
    except ValueError as e:
        return False
    return True



def main():
   

    file_list = glob.glob("queries/*.json")
    for in_file in file_list:
        if is_valid_json(open(in_file, "r").read()) == False:
            print ("ERROR: invalid json file %s" % (in_file))
            continue
        test_obj_dict = json.loads(open(in_file, "r").read())
        for api_name in test_obj_dict:
            test_obj = test_obj_dict[api_name]
            res_file = "responses/%s.json" % (api_name)
            if os.path.isfile(res_file) == False:
                print ("ERROR: response file %s not found" % (res_file))
                continue
            if "schemafile" not in test_obj:
                print ("ERROR: schema path not given for response file %s" % (res_file))
                continue
            schema_file = test_obj["schemafile"]
            print ("Creating %s ... " % (schema_file))
            res_obj = json.loads(open(res_file,"r").read())
            builder = SchemaBuilder()
            builder.add_object(res_obj)
            schema_obj = builder.to_schema()
            with open(schema_file, "w") as FW:
                FW.write("%s\n" % (json.dumps(schema_obj, indent=4)))
            print ("done!")



if __name__ == '__main__':
    main()





