import json

doc = json.loads(open("junk", "r").read())

for k in doc["by_subject"]:
    obj = doc["by_subject"][k]
    #if k in ["P14210-1"]:
    if k in ["Q5EBA7-1"]:
        #print (json.dumps(obj, indent=4))
        print (list(obj.keys()))




