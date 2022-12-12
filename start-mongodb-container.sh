if [ -z "$1" ]
then
    echo ""
    echo "no server speficified!"
    echo ""
    exit
fi

server=$1
network="glygen_backend"
mongo_port="7070"

mongo_container="running_glygen_mongo_"$server
api_container="running_glygen_"$server"_api"

e_params="-e MONGO_INITDB_ROOT_USERNAME=superadmin -e MONGO_INITDB_ROOT_PASSWORD=superpass"

docker rm -f $mongo_container
docker rm -f $api_container
docker network rm  $network

docker network create -d bridge $network

docker run --name $mongo_container --network $network -p 127.0.0.1:$mongo_port:27017 -d -v /data/shared/glygen/db:/data/shared/glygen/db/$server $e_params mongo


