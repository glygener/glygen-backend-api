import os,sys
import string
from optparse import OptionParser
import glob
import json
import subprocess

__version__="1.0"
__status__ = "Dev"



###############################
def main():


    config_obj = json.loads(open("./conf/config.json", "r").read())
    image = "glyomics/substructure"
    network = config_obj["dbinfo"]["bridge_network"]
    port="10980"
    container_name = "running_substructure"

    cmd_list = []
    cmd_list.append("sudo systemctl stop docker-glygen-substructure.service") 
    cmd = "docker create --name %s --network %s -p %s:%s" % (container_name, network, port, port)
    cmd += " -e WEBSERVICE_BASIC_PORT=%s -e WEBSERVICE_BASIC_MAX_CPU_CORE=3 %s " % (port, image)
    cmd_list.append(cmd)


    for cmd in cmd_list:
        x = subprocess.getoutput(cmd)
        print (x)



if __name__ == '__main__':
    main()
