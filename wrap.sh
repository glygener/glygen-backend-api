#srv="prd"
#srv="beta"
srv="tst"


sudo systemctl stop docker-glygen-api-$srv.service
python3 create_api_container.py -s $srv
sudo systemctl start docker-glygen-api-$srv.service


docker volume prune -a -f
docker buildx prune -a -f
docker builder prune -a -f


