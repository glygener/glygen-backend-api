import os,sys
import string
from optparse import OptionParser
import glob
import json
import subprocess
import socket

__version__="1.0"
__status__ = "Dev"


def make_files(host_vm):

    out_file = "./substructure-local.ini"
    line_list = ["[basic]", "port = 10983","max_cpu_core = 3","[Substructure]","max_motif_size = 10","glycan_set = glygen"]
    with open(out_file, "w") as FW:
        for line in line_list:
            FW.write("%s\n" % (line))
    out_file = "./docker-compose.yml"
    line_list = [
         "services:"
        ,"  cache-permissions:"
        ,"    image: alpine:3.20"
        ,"    user: \"0:0\""
        ,"    command: [\"sh\", \"-c\", \"chown -R 10001:10001 /cache\"]"
        ,"    volumes:"
        ,"      - substructure-cache:/cache"
        ,"    restart: \"no\""
        ,"  substructure:"
        ,"    container_name: running_glygen_substructure"
        ,"    restart: unless-stopped"
        ,"    image: glyomics/substructure:latest"
        ,"    user: 10001:10001"
        ,"    depends_on:"
        ,"      cache-permissions:"
        ,"        condition: service_completed_successfully" 
        ,"    ports:"
        ,"      - 10983:10983"
        ,"    volumes:"
        ,"      - ./substructure-local.ini:/code/substructure-local.ini"
        ,"      - substructure-cache:/data/shared/glygen/substrcture/%s/cache/" % (host_vm)
        ,"    networks:"
        ,"      - glygen_backend"
        ,""
        ,"volumes:"
        ,"  substructure-cache:"
        ,""
        ,"networks:"
        ,"  glygen_backend:"
        ,"    external: true"
    ]






    with open(out_file, "w") as FW:
        for line in line_list:
            FW.write("%s\n" % (line))
    

    return


###############################
def main():


        
    host_name = socket.gethostname()
    host_vm = host_name.split("-")[-1]




    config_obj = json.loads(open("./conf/config.json", "r").read())
    image = "glyomics/substructure"
    port = config_obj["ss_port"]
    container_name = "running_glygen_substructure"
    network = "host"

    make_files(host_vm)

    cmd_list = []
    cmd_list.append("sudo systemctl stop docker-glygen-substructure.service")

    cmd = "docker ps --all |grep %s" % (container_name)
    container_id = subprocess.getoutput(cmd).split(" ")[0].strip()
    if container_id.strip() != "":
        cmd_list.append("docker rm -f %s " % (container_id))

    cmd_list.append("docker compose up -d")
 
    cmd_list.append("sudo systemctl start docker-glygen-substructure.service")

    for cmd in cmd_list:
        subprocess.run(cmd, shell=True)
        print (cmd)



if __name__ == '__main__':
    main()
