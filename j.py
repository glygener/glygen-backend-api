import json

doc = json.load(open("junk.json"))

for obj in doc["results"]:
    print (obj["record_id"],obj["reported_snv"])

