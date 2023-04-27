import os,sys
import string
from optparse import OptionParser
import glob
import json
from bson import json_util
import pymongo
from pymongo import MongoClient
import datetime
import pytz
import subprocess

def main():

    #in_file = "/data/shared/glygen/releases/data/v-2.0.3/jsondb/proteindb/P14210-1.json"
    #obj = json.loads(open(in_file, "r").read())
    #print (json.dumps(list(obj.keys()), indent=4))

    field_map = json.loads(open("./glygen/conf/fieldmap.json", "r").read())
    
    obj = json.loads(open("./glygen/conf/section.1.json", "r").read())    
    for record_type in obj:
        for sec in obj[record_type]:
            obj[record_type][sec]["sectionfield"] = field_map[record_type][sec]["sectionfield"]
            tmp_list = []
            for k in obj[record_type][sec]["fieldmap"]:
                o = obj[record_type][sec]["fieldmap"][k]
                oo = {"path":o["id"], "label":o["label"]}
                tmp_list.append(oo)
            obj[record_type][sec]["fieldmap"] = tmp_list

            if record_type == "protein":
                if sec == "glycosylation_reported_with_glycans":
                    obj[record_type][sec]["filterinfo"] = {
                        "field": "site_category",
                        "value": "reported_with_glycan"
                    }
                elif sec == "glycosylation_reported":
                    obj[record_type][sec]["filterinfo"] = {
                        "field": "site_category",
                        "value": "reported"
                    }


    print (json.dumps(obj,indent=4))    




if __name__ == '__main__':
    main()
