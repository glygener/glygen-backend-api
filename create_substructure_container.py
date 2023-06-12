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


    usage = "\n%prog  [options]"
    parser = OptionParser(usage,version="%prog version___")
    parser.add_option("-s","--server",action="store",dest="server",help="dev/tst/beta/prd")
    (options,args) = parser.parse_args()

    for key in ([options.server]):
        if not (key):
            parser.print_help()
            sys.exit(0)

    server = options.server


    config_obj = json.loads(open("./conf/config.json", "r").read())
    image = "glyomics/substructure"
    network = config_obj["dbinfo"]["bridge_network"] 
    if server in ["beta", "prd"]:
        network = config_obj["dbinfo"]["bridge_network"] + "_" + server
    port = config_obj["ss_port"][server]
    container_name = "running_substructure"
    if server in ["beta"]:
        container_name = "running_substructure_%s" % (server)    

    cmd_list = []
    cmd_list.append("sudo systemctl stop docker-glygen-substructure-%s.service" % (server)) 
    cmd = "docker create --name %s --network %s -p %s:%s" % (container_name, network, port, port)
    cmd += " -e WEBSERVICE_BASIC_PORT=%s -e WEBSERVICE_BASIC_MAX_CPU_CORE=3 %s " % (port, image)
    cmd_list.append(cmd)


    for cmd in cmd_list:
        x = subprocess.getoutput(cmd)
        print (x)



if __name__ == '__main__':
    main()
