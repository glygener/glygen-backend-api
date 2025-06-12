import sys,os
import json
import string
import glob
from genson import SchemaBuilder
from optparse import OptionParser



def main():

    usage = "\n%prog  [options]"
    parser = OptionParser(usage,version="%prog version___")
    parser.add_option("-i","--infile",action="store",dest="infile",help="")
    parser.add_option("-o","--outfile",action="store",dest="outfile",help="")
    
    (options,args) = parser.parse_args()
    for key in ([options.infile, options.outfile]):
        if not (key):
            parser.print_help()
            sys.exit(0)

    in_file = options.infile
    out_file = options.outfile

    in_obj = json.loads(open(in_file,"r").read())
    builder = SchemaBuilder()
    builder.add_object(in_obj)
    out_obj = builder.to_schema()
     
    with open(out_file, "w") as FW:
        FW.write("%s\n" % (json.dumps(out_obj, indent=4)))
           
    exit()



    #file_list = glob.glob("queries/*.json")
    file_list = ["queries/toy.json"]

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

            schema_file = test_obj["schemafile"] + "-auto"

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





