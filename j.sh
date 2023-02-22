server="tst"
db_user="glydbadmin"
db_pass="glydbpass"
db_name="glydb"
archive_file="/data/shared/glygen/mongodump/archive"


docker exec -it running_glygen_mongo_tst mongorestore --username $db_user --password $db_pass --authenticationDatabase=glydb --archive=$archive_file --drop --nsFrom='tmpdb.*' --nsTo='glydb.*'


