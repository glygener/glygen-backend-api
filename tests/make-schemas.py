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
   
    api_name = "glycan_search_init"
    res_file = "responses/%s.json" % (api_name)
    if os.path.isfile(res_file) == False:
        print ("ERROR: response file %s not found" % (res_file))
        exit()
    res_obj = json.loads(open(res_file,"r").read())
    builder = SchemaBuilder()
    builder.add_object(res_obj)
    schema_obj = builder.to_schema()
    print(json.dumps(schema_obj, indent=4))


if __name__ == '__main__':
    main()





