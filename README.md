## Setting config parameters
After cloning this repo, you will need to set the paramters given in
conf/config.json


## Data dependence
Download data release from https://data.glygen.org/ftp/ and unpack it in
your host server under:

{DATA_PATH}/releases/data/v-{VER}/

where {VER} is the version label for the data release (e.g 2.0.2).

You will also need to create the following paths in your host server:

{DATA_PATH}/logs/
{DATA_PATH}/userdata/{SERVER}/jobs/

where DATA_PATH and SERVER are specified in your conf/config.json



## Starting the mongodb container

Run the python script given to build and start a mongodb container:

#### `python3 start_mongodb_container.py`



## Initialize and populate your mongodb database

To init your mongodb, run:

#### `python3 init_mongodb.py`

this should be done only one time. 

You can populate the database partially (for test purposes) or fully using
the following commands:

#### `python3 load_objects.py -v {VER} -m partial`
#### `python3 load_objects.py -v {VER} -m full`

where {VER} is the version label for the data release (e.g 2.0.2).



## Building and starting the docker container for the APIs

Run the python script given to build and start container:

#### `python3 start_api_container.py`






## Testing APIs
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




