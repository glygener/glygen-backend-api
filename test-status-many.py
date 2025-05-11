import json
import requests
import subprocess
import time
import random
in_file = "tests/examples/job/job_addnew.isoform_mapper.x.json"
doc = json.load(open(in_file))
#doc["intable"][-1][1] = str(int(doc["intable"][-1][1]) + 1)
s = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
idx = random.randint(0, len(s))
doc["intable"][-1][1] = s[idx]
with open(in_file, "w") as FW:
    FW.write("%s\n" % (json.dumps(doc, indent=4)))

cmd = "http POST :4442/job/addnew/ < tests/examples/job/job_addnew.isoform_mapper.x.json"
res = subprocess.getoutput(cmd)
res_obj = json.loads(res)
job_id_one = res_obj["jobid"]

#print (json.dumps(res_obj, indent=4))

in_file = "tests/examples/job/job_addnew.structure.x.json"
doc = json.load(open(in_file))
doc["parameters"]["seq"] += "\n" + s[idx]
with open(in_file, "w") as FW:
    FW.write("%s\n" % (json.dumps(doc, indent=4)))

cmd = "http POST :4442/job/addnew/ < tests/examples/job/job_addnew.structure.x.json"
res = subprocess.getoutput(cmd)
res_obj = json.loads(res)
job_id_two = res_obj["jobid"]

print (json.dumps(res_obj, indent=4))


#time.sleep(5)

in_file = "tests/examples/job/job_status_many.json"
doc = {"jobidlist":[job_id_one, job_id_two]}
with open(in_file, "w") as FW:
    FW.write("%s\n" % (json.dumps(doc, indent=4)))
cmd = "http POST :4442/job/status_many/ < tests/examples/job/job_status_many.json"
res = subprocess.getoutput(cmd)
res_obj = json.loads(res)
print (json.dumps(res_obj, indent=4))





