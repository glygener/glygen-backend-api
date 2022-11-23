mod="glygen"
ver="1.0"
server="tst"
container="running_"$mod"_"$server"_api"
port="8082"
#port="8882" #for beta

python3 setup.py bdist_wheel $mod $ver

##################################################################
# maintain customized versions of the config file for each server
# following instance/config.dev.py, and keep these versions in 
# private folder
##############################################################

cp private/config.glygen_$server.py instance/config.prd.py 
docker build --network=host -t "$mod"_"$server"_api .
rm instance/config.prd.py

docker rm -f $container

sudo docker run -dit --name $container -p 127.0.0.1:$port:80 -v /data/shared/$mod:/data/shared/$mod "$mod"_"$server"_api
