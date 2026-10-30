image="glygen_api"
container="running_"$image
port="4042"

#python3 setup.py bdist_wheel 
#docker build --network=host -t $image .
#docker rm -f $container

docker run -dit --name $container -p 127.0.0.1:$port:80 -v /data/shared/glygen:/data/shared/glygen $image

