## Requirements
The following python modules must be available on your server:

* pymongo
* jsonref
* jsonschema


## Setting config parameters
After cloning this repo, you will need to set the paramters given in
conf/config.json


## Step-1: Data download
Visit https://data.glygen.org/ftp/ to see what data release/version {VER} you want to 
download (for example 2.0.2), and run the python script given to download from
that release. Since this will take long, use nohup as shown below.

#### `nohup python3 download_data.py -v {VER} > logfile.log & `



## Step-2: Starting the mongodb container
Run the python script given to build and start a mongodb container:

#### `python3 start_mongodb_container.py`



## Step-3: Initialize and populate your mongodb database
To init your mongodb, run (this should be done only one time):


#### `python3 init_mongodb.py`

You can populate the database partially (for test purposes) or fully using
the following commands:

#### `python3 load_objects.py -v {VER} -m partial`
#### `python3 load_objects.py -v {VER} -m full`



## Step-4: Building and starting the docker container for the APIs
Run the python script given to build and start container:

#### `python3 start_api_container.py`



## Step-5: Testing APIs
The script tests/run_api_test.py is a wrapper outside of the container 
that allows you to test APIs in an automated manner. 

Before running, you will need to set some paramters in the 
conf/config.json file.

### API tests using example queries
To test a group of APIs using the example queries given in 
tests/queries/protein.json, run:

#### python3 run_api_test.py -m 1 -g $grp

where $grp can one of [protein, glycan, motif ...]. This will produce 
the following log files ($username is your ssh login user name):

{DATA_PATH}/logs/$username_test_summary_$grp_mode_1.csv (status of each call)
{DATA_PATH}/logs/$username_failure_log_$grp*.json (details for failed calls)


### Exhaustive tests for record/detail APIs
Some of our APIs are called "detail APIs" because the return detailed
information about a given record. To test such APIs for a given API group:

#### python3 run_api_test.py -m 2 -g $grp

where $grp can one of [protein, glycan, motif ...]. This will produce 
the following log files ($username is your ssh login user name):

{DATA_PATH}/logs/$username_test_summary_$grp_mode_2.csv (status of each call)
{DATA_PATH}/logs/$username_failure_log_$grp_detail.*.json (details for failed calls)




