import os,sys
import string
import glob
import json
import subprocess



###############################
def main():

    doc = json.load(open("junk"))
    for obj in doc:
        print (obj["id"])
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
