import os,sys
import string
import glob
import json
import subprocess

def get_path_value(path, obj):

    p_list = path.split(".")
    val_obj = obj
    for p in p_list:
        if type(val_obj) is dict:
            val_obj = val_obj[p]
        elif type(val_obj) is list:
            tmp_list = []
            for val in val_obj:
                if type(val) is dict:
                    if type(val[p]) in [int, float, str]:
                        tmp_list.append(str(val[p]))
            val_obj = ";".join(tmp_list)
    return val_obj



###############################
def main():

    doc = json.load(open("glygen/conf/config.json"))
    print (json.dumps(doc, indent=4))
    exit()


    obj = {
        "proteins":{
            "protein_names": [
                {
                    "name": "Tumor necrosis factor receptor superfamily member 11B",
                    "resource": "UniProtKB",
                    "type": "recommended"
                },
                {
                    "name": "Osteoclastogenesis inhibitory factor",
                    "resource": "UniProtKB",
                    "type": "synonym"
                }
            ]
        }
    }

    path = "proteins.protein_names.name"
    val_obj = get_path_value(path, obj)
    print (val_obj)
    exit()    


    doc = json.load(open("junk1"))
    for obj in doc["results"]:
        print ("1",obj["disease_id"], obj["recommended_name"])
     
    doc = json.load(open("junk2"))
    for obj in doc["results"]:
        print ("2",obj["disease_id"], obj["recommended_name"])

    exit()

    file_list = glob.glob("glygen/*.py")
    for in_file in file_list:
        file_name = in_file.split("/")[-1]
        sbr = ""
        with open(in_file, "r") as FR:
            for line in FR:
                if line[0:4] == "def ":
                    sbr = line.split("(")[0].split(" ")[1]
                if line.find("get_mongodb") != -1:
                    print (file_name, sbr)    
    exit()


    cmd = "http POST :8082/protein/detail/P14210-1/"
    for i in range(0, 10):
        x = subprocess.getoutput(cmd)
        print (i)


if __name__ == '__main__':
    main()
