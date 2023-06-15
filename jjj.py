import json

doc = json.loads(open("junk", "r").read())
print (json.dumps(doc, indent=4))
