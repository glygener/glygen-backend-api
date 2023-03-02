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
    server = config_obj["server"]

    image = "glygen_%s_api" % (server) 
    api_container = "running_" + image
    mongo_container = "running_glygen_mongo_" + server
    port = config_obj["api_port"]
    data_path = config_obj["data_path"]
    network = config_obj["dbinfo"]["bridge_network"]
    mongo_user = config_obj["dbinfo"]["glydb"]["user"]
    mongo_password = config_obj["dbinfo"]["glydb"]["password"]
    mongo_db =  config_obj["dbinfo"]["glydb"]["db"]
    mail_server = config_obj["mail"]["server"]
    mail_port = config_obj["mail"]["port"]
    mail_sender = config_obj["mail"]["sender"]

    conn_str = "mongodb://%s:%s@%s:27017/?authSource=%s" % (mongo_user, mongo_password, mongo_container, mongo_db)
    cmd_list = []
    if os.path.isdir(data_path) == False:
        cmd_list.append("mkdir -p %s" % (data_path))

    cmd_list.append("python3 setup.py bdist_wheel")
    cmd_list.append("docker build --network=host -t %s ." % (image))
    for c in [api_container]:
        cmd = "docker ps |grep %s" % (c)
        x = subprocess.getoutput(cmd).split(" ")[-1].strip()
        if x == c:
            cmd_list.append("docker rm -f %s " % (c))

    cmd = "docker run -dit --name %s --network %s -p 127.0.0.1:%s:80" % (api_container, network, port)
    cmd += " -v %s:%s -e MONGODB_CONNSTRING=%s -e DB_NAME=%s " % (data_path, data_path, conn_str, mongo_db)
    cmd += " -e MAIL_SERVER=%s -e MAIL_PORT=%s -e MAIL_SENDER=%s -e DATA_PATH=%s -e SERVER=%s %s" % (mail_server, mail_port, mail_sender, data_path, server, image) 
    
    cmd_list.append(cmd)



    for cmd in cmd_list:
        x = subprocess.getoutput(cmd)
        print (x)



if __name__ == '__main__':
    main()
