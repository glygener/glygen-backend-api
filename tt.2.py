import json
import requests


input_dict = {
    "glycan":{"payload":{"id":"8ced125ef3720464f566a44cd6076aba"}, "url":"https://api.glygen.org/glycan/list/"},
    "protein":{"payload":{"id":"c555caa41ea6433c5a6125d2d701756c"}, "url":"https://api.glygen.org/protein/list/"}
}


record_type = "protein"
url = input_dict[record_type]["url"]
payload = input_dict[record_type]["payload"]
response = requests.post(url, json=payload, verify=False)
response_json = json.loads(response.content)

print (json.dumps(response_json, indent=4))






