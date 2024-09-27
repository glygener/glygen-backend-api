import json

in_file = "tmp/junk.json"
doc = json.loads(open(in_file, "r").read())

for obj in doc["snv"]:
    flag = "disease" in obj
    print (obj["start_pos"], flag, obj["keywords"])

