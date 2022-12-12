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


    
    api_container = "running_glygen_%s_api" % (server)
    mongo_container = "running_glygen_mongo_%s" % (server)
    mongo_network = config_obj["dbinfo"]["bridge_network"]
    mongo_port = config_obj["dbinfo"]["port"]


    u, p = config_obj["dbinfo"]["admin"]["user"], config_obj["dbinfo"]["admin"]["password"]
    e_params = "-e MONGO_INITDB_ROOT_USERNAME=%s -e MONGO_INITDB_ROOT_PASSWORD=%s" % (u, p)

    cmd_list = []
    for c in [mongo_container, api_container]:
        cmd = "docker ps |grep %s" % (c)
        x = subprocess.getoutput(cmd).split(" ")[-1].strip()
        if x == c:
            cmd_list.append("docker rm -f %s " % (c))
    
    cmd = "docker network ls| grep %s" % (mongo_network)
    x = subprocess.getoutput(cmd).split()[1]
    if x == mongo_network:
        cmd_list.append("docker network rm %s | true" % (mongo_network))
    
    cmd_list.append("docker network create -d bridge %s" % (mongo_network))
    cmd = "docker run --name %s --network %s -p 127.0.0.1:%s:27017" % (mongo_container, mongo_network,mongo_port)
    cmd += " -d -v /data/shared/glygen/db:/data/shared/glygen/db/%s %s mongo" % (server, e_params)
    cmd_list.append(cmd)

    for cmd in cmd_list:
        x = subprocess.getoutput(cmd)
        print (x)



if __name__ == '__main__':
    main()
