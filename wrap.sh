ver="2.0.2"
python3 start_mongodb_container.py
python3 init_mongodb.py
python3 start_api_container.py
nohup python3 load_objects.py -v $ver -m full > logfile &



