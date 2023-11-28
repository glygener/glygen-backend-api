## Requirements
The following python modules must be available on your server:

* pymongo
* jsonref
* jsonschema


## Setting config parameters
After cloning this repo, you will need to set the paramters given in
conf/config.json. Make sure you are in the branch for the given release.
For example, you are trying to deploy release 2.0, use the following 
commands to be in the right branch.
   ```
   git checkout 2.2
   git branch
   ```
the second command should show that you are are in 2.0 branch.



## Step-1: Data download
Visit https://data.glygen.org/ftp/ to see what data release/version $VER you want to 
download (for example 2.0.2), and run the python script given to download from
that release. Since this will take long, use nohup as shown below.

   ```
   nohup python3 download_data.py -v $VER > logfile.log & 
   ```


## Step-2: Creating and starting docker container for mongodb
Run the python script given to create a mongodb container with admin
authentication creditials given in the conf/config.json file.
   ```
   python3 create_mongodb_container.py -s $SER
   docker ps --all 
   ```
where $SER is your deployment server which can be  dev, tst, beta or prd.
The last command should list docker all containers and you should see the container
you created 'running_glygen_mongo_$SER'. To start this container, the best way is
to create a service file (/usr/lib/systemd/system/docker-glygen-mongo-$SER.service),
and place the following content in it. 
   ```
   [Unit]
   Description=Glygen MONGODB Container ($SER)
   Requires=docker.service
   After=docker.service

   [Service]
   Restart=always
   ExecStart=/usr/bin/docker start -a running_glygen_mongo_$SER
   ExecStop=/usr/bin/docker stop -t 2 running_glygen_mongo_$SER

   [Install]
   WantedBy=default.target
   ```

This will allow you to start/stop the container with the following commands, and ensure
that the container will start on server reboot.
   ```
   $ sudo systemctl daemon-reload 
   $ sudo systemctl enable docker-glygen-mongo-$SER.service
   $ sudo systemctl start docker-glygen-mongo-$SER.service
   $ sudo systemctl stop docker-glygen-mongo-$SER.service
   ```


## Step-3: Initialize and populate your mongodb database
 Run the command given below to create the "glydb" database and glydb user
(this should be done only one time). 
   ```
   python3 init_mongodb.py -s $SER
   ```
You can populate collections using the following commands:
   ```
   python3 populate_collections.py -s $SER -v $VER
   ```
To update a few collections, you can use:
   ```
   python3 populate_collection.py -s $SER -v $VER -c $COLLS
   ```
where the variable $COLLS is collection names separated by comma (e.g., c_glycan,c_motif)



## Step-4: Creating and starting docker container for mongodb
Run the python script given to build and create the API container:
   ```
   python3 create_api_container.py -s $SER
   docker ps --all 
   ```
where $SER is your deployment server which can be  dev, tst, beta or prd.
The last command should list docker all containers and you should see the container
you created "running_glygen_api_$SER". To start this container, the best way is
to create a service file (/usr/lib/systemd/system/docker-glygen-api-$SER.service),
and place the following content in it. 
   ```
   [Unit]
   Description=Glygen API Container ($SER)
   Requires=docker.service
   After=docker.service

   [Service]
   Restart=always
   ExecStart=/usr/bin/docker start -a running_glygen_api_$SER
   ExecStop=/usr/bin/docker stop -t 2 running_glygen_api_$SER

   [Install]
   WantedBy=default.target
   ```

This will allow you to start/stop the container with the following commands, and ensure
that the container will start on server reboot.
   ```
   $ sudo systemctl daemon-reload 
   $ sudo systemctl enable docker-glygen-api-$SER.service
   $ sudo systemctl start docker-glygen-api-$SER.service
   $ sudo systemctl stop docker-glygen-api-$SER.service
   ```


## Step-5: Updating supersearch init 
This will perform supersearch API calls for each concept type and
update the collection "c_searchinit"
   ```
   python3 update-search-init.py -s tst
   ```


## Step-6: Creating and docker container for substructure search tool
Run the python script given to build and create the API container:
   ```
   python3 create_substructure_container.py 
   docker ps --all 
   ```
where $SER is your deployment server which can be  dev, tst, beta or prd.
The last command should list docker all containers and you should see the container
you created "running_substructure". To start this container, the best way is
to create a service file (/usr/lib/systemd/system/docker-glygen-substructure-$SER.service),
and place the following content in it. 
   ```
   [Unit]
   Description=Glygen Substructure Container
   Requires=docker.service
   After=docker.service

   [Service]
   Restart=always
   ExecStart=/usr/bin/docker start -a running_substructure
   ExecStop=/usr/bin/docker stop -t 2 running_substructure

   [Install]
   WantedBy=default.target
   ```

This will allow you to start/stop the container with the following commands, and ensure
that the container will start on server reboot.
   ```
   $ sudo systemctl daemon-reload 
   $ sudo systemctl enable docker-glygen-substructure-$SER.service
   $ sudo systemctl start docker-glygen-substructure-$SER.service
   $ sudo systemctl stop docker-glygen-substructure-$SER.service
   ```


## Step-7: Testing APIs
The script tests/run_api_test.py is a wrapper outside of the container 
that allows you to test APIs in an automated manner. Before running, you will 
need to set some paramters in the conf/config.json file.

### API tests using example queries
To test a group of APIs using the example queries given in 
tests/queries/protein.json, run:
   ```
   python3 run_api_test.py -m 1 -g $grp
   ```
where $grp can one of [protein, glycan, motif ...]. This will produce 
the following log files ($username is your ssh login user name):
   ```
   $DATA_PATH/logs/$username_test_summary_$grp_mode_1.csv (status of each call)
   $DATA_PATH/logs/$username_failure_log_$grp*.json (details for failed calls)
   ```

### Exhaustive tests for record/detail APIs
Some of our APIs are called "detail APIs" because the return detailed
information about a given record. To test such APIs for a given API group:
   ```
   python3 run_api_test.py -m 2 -g $grp
   ```
where $grp can one of [protein, glycan, motif ...]. This will produce 
the following log files ($username is your ssh login user name):
   ```
   $DATA_PATH/logs/$username_test_summary_$grp_mode_2.csv (status of each call)
   $DATA_PATH/logs/$username_failure_log_$grp_detail.*.json (details for failed calls)
   ```


### Customization of Swagger page
Edit /data/shared/glygen/swagger/swagger-ui.html first and then get into the API container to copy this file
into /usr/local/lib/python3.6/site-packages/flask_restx/templates/ folder in the container. The command below
assume that you have /data/shared/glygen/swagger/ visible from the container.

```
docker exec -it running_glygen_api_$SER bash
cp /data/shared/glygen/swagger/swagger-ui.html /usr/local/lib/python3.6/site-packages/flask_restx/templates/swagger-ui.html
exit
sudo systemctl restart docker-glygen-api-$SER.service
```


