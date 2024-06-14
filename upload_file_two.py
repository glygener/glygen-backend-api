import json
import requests
from requests.packages.urllib3.filepost import encode_multipart_formdata


url = "http://localhost:8082/job/addnew/"
in_file = "tmp/input.csv"
files = {"userfile": open(in_file, 'rb')}
req_obj = {}
res = requests.post(url, files=files, data=req_obj)
res_obj = json.loads(res.content)
print (json.dumps(res_obj, indent=4))



