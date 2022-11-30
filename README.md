## Building and starting docker container

After cloning, copy instance/config.dev.py to instance/config.py 
and set config paramters for your production server.

Then, run the shell script given to build and start container:

#### `sh start-container.sh`


## Data dependence
Download data release from https://data.glygen.org/ftp/ and unpack it in 
your host server under:

{DATA_PATH}/releases/data/ 

You will also need to create the following path in your host server:

{DATA_PATH}/userdata/{SERVER}/jobs/

where DATA_PATH and SERVER are specified in your instance/config.py


## Testing APIs
Go to the "tests" folder and run:

#### python3 run_api_test.py -





