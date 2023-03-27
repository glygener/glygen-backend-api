server="tst"
db_user="glydbadmin"
db_pass="glydbpass"
db_name="glydb"
dump_dir="/data/shared/glygen/mongodump/"


docker exec running_glygen_mongo_beta mongorestore --username $db_user --password $db_pass --db $db_name $dump_dir/tmpdb --drop

