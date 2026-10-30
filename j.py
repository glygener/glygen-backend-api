import json

doc = json.load(open("junk.json"))
print (json.dumps(doc["filters"], indent=4))
exit()
for obj in doc["results"]:
    print (obj["keywords"])

