import json

doc = json.load(open("junk"))

print (json.dumps(doc["filters"]["available"][0], indent=4))
exit()

for obj in doc["results"]:
    print (obj["hit_score"])

