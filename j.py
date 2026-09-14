import json

doc = json.load(open("junk.json"))

#print (doc["cache_info"])
#exit()

for obj in doc["results"]:
    print (obj["record_id"])


