import json
import requests


input_dict = {
    "glycan":{"url":"https://api.glygen.org/glycan/detail/G17689DH/"},
    "protein":{"url":"https://api.glygen.org/protein/detail/P14210/"}
}

record_type = "protein"
url = input_dict[record_type]["url"]
payload = {}
response = requests.post(url, json=payload, verify=False)
response_json = json.loads(response.content)

print (json.dumps(response_json, indent=4))






