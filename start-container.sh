mod="glygen"
ver="1.0"
server="tst"
container="running_"$mod"_"$server"_api"
port="8082"
#port="8882" #for beta

docker build --network=host -t "$mod"_"$server"_api .
exit;

docker rm -f $container

sudo docker run -dit --name $container -p 127.0.0.1:$port:80 -v /data/shared/$mod:/data/shared/$mod "$mod"_"$server"_api
