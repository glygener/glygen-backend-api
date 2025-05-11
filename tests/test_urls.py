import sys,os
import json
import string
import traceback
from optparse import OptionParser
import requests
import glob
import random
import urllib3

urllib3.disable_warnings()



def main():
   
    usage = "\n%prog  [options]"
    parser = OptionParser(usage,version="%prog version___")
    parser.add_option("-v","--dataversion",action="store",dest="dataversion",help="2.8.1")
        

    (options,args) = parser.parse_args()
    for key in ([options.dataversion]):
        if not (key):
            parser.print_help()
            sys.exit(0)

    ver = options.dataversion
    file_list = glob.glob("/data/shared/glygen/releases/data/v-%s/jsondb/urldb/*.csv" % (ver))
    url_dict = {}
    for in_file in file_list:
        with open(in_file, "r") as FR:
            for url in FR:
                url = url.strip()
                domain = url.split("/")[2]
                if domain not in url_dict:
                    url_dict[domain] = {}
                url_dict[domain][url] = True
   
    selected_dict = {}
    sample_size = 10     
    for domain in url_dict:
        url_list = list(url_dict[domain].keys())
        n = len(url_list)
        if n < sample_size:
            selected_dict[domain] = url_list
        else:
            selected_dict[domain] = []
            for i in range(0, sample_size):
                idx = random.randint(0, n-1)
                selected_dict[domain].append(url_list[idx])


    for domain in selected_dict:
        for url in selected_dict[domain]:
            res = requests.get(url, json={}, verify=False)
            print (res.status_code, domain, url)
    

    return






if __name__ == '__main__':
    main()





