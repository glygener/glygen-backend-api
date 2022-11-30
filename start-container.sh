server="tst"
image="glygen_"$server"_api"
container="running_"$image
port="8082"
#port="8882" #for beta

python3 setup.py bdist_wheel 

##################################################################
# maintain customized versions of the config file for each server
# following instance/config.dev.py, and keep these versions in 
# private folder
##############################################################

cp private/config.glygen_$server.py instance/config.py 
docker build --network=host -t $image .
rm instance/config.py

docker rm -f $container

sudo docker run -dit --name $container -p 127.0.0.1:$port:80 -v /data/shared/glygen:/data/shared/glygen $image

