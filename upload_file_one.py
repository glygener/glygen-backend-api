import requests
from requests.packages.urllib3.filepost import encode_multipart_formdata


url = "http://localhost:8082/idmapping/search/"
in_file = "foo.txt"
files = {"userfile": open(in_file, 'rb')}
req_obj = {
    "recordtype":"protein",
    "input_namespace":"UniProtKB",
    "output_namespace":"GeneID",
    "input_idlist":"M9PJ12,Q9VRR2"
}
r = requests.post(url, files=files, data=req_obj)

print (r.content)



