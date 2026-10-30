
sudo systemctl stop docker-glygen-api.service
python3 create_api_container.py 
sudo systemctl start docker-glygen-api.service


#docker volume prune -a -f
#docker buildx prune -a -f
#docker builder prune -a -f


