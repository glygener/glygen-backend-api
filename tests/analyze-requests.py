import sys,os
import json
import string
import traceback
from optparse import OptionParser
import requests
import glob
import subprocess
import test_lib




def main():

    file_list = glob.glob("/data/shared/glygen/archive/c_request-2024-*.json") 
    for in_file in file_list:
        doc = json.loads(open(in_file, "r").read())
        idx = 0
        count_dict = {"all":{}}
        for obj in doc:
            #print (json.dumps(obj, indent=4))
            #exit()
            idx += 1
            ts, api = obj["ts"], obj["api"]
            mm = ts.split(":")[0] + ":" + ts.split(":")[1]
            sec = int(ts.split(":")[-1].split(" ")[0])
            sec_idx = int(sec/5) + 1
            c = "%s|%s" % (mm, sec_idx)
            if api not in count_dict:
                count_dict[api] = {}
            if c not in count_dict[api]:
                count_dict[api][c] = 0
            count_dict[api][c] += 1
            if c not in count_dict["all"]:
                count_dict["all"][c] = 0
            count_dict["all"][c] += 1 
        for api in count_dict:
            mx, mx_c = 0, ""
            for c in count_dict[api]:
                n = count_dict[api][c]
                if n > mx:
                    mx, mx_c = n, c
            print (mx, mx_c, api)

    return






if __name__ == '__main__':
    main()





