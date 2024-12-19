import json
import requests
from requests.packages.urllib3.filepost import encode_multipart_formdata


#in_file = "/data/shared/glygen/releases/data/v-2.5.1/reviewed/chicken_protein_ntdata.nt"
in_file = "tmp/input.2.csv"

url = "http://localhost:8082/job/addnew/"
#url = "http://localhost:8082/idmapping/search/"



req_obj_one = {
    "parameters":{},
    "zzzz":"dfafa",
    "jobtype":"isoform_mapper"
}
req_obj_two = {
    "recordtype":"protein",
    "input_namespace":"UniProtKB",
    "output_namespace":"GeneID",
    "input_idlist":"M9PJ12,Q9VRR2"
}

req_obj = req_obj_one
#files = {
#    "data":json.dumps(req_obj),
#    "userfile": open(in_file, 'rb')
#}
files = {
    "userfile": open(in_file, 'rb')
}

res = requests.post(url, files=files, data=req_obj)
res_obj = json.loads(res.content)
print (res.status_code)
print (json.dumps(res_obj, indent=4))





