import sys,os
import json
import requests
import datetime
import pytz
import warnings
from urllib3.exceptions import InsecureRequestWarning
warnings.simplefilter("ignore", InsecureRequestWarning)




def get_req_obj_list():

    obj_list = [
        {"id":"O14686-1", "size":"14M", "type":"protein"}
        ,{"id":"Q8WZ42-1", "size":"14M", "type":"protein"}
        ,{"id":"O14497-1", "size":"11M", "type":"protein"}
        ,{"id":"P68431-1", "size":"11M", "type":"protein"}
        ,{"id":"P42336-1", "size":"11M", "type":"protein"}
        ,{"id":"Q8WXI7-1", "size":"11M", "type":"protein"}
        ,{"id":"Q8NEZ4-1", "size":"11M", "type":"protein"}
        ,{"id":"P60484-1", "size":"9.9M", "type":"protein"}
        ,{"id":"Q99102-1", "size":"9.7M", "type":"protein"}
        ,{"id":"pubmed.31373491", "size":"15M", "type":"publication"}
        ,{"id":"pubmed.25561503", "size":"15M", "type":"publication"}
        ,{"id":"pubmed.22661428", "size":"15M", "type":"publication"}
        ,{"id":"pubmed.21740066", "size":"15M", "type":"publication"}
        ,{"id":"pubmed.19651622", "size":"15M", "type":"publication"}
        ,{"id":"pubmed.37217939", "size":"15M", "type":"publication"}
        ,{"id":"pubmed.17081983", "size":"14M", "type":"publication"}
        ,{"id":"pubmed.21183079", "size":"14M", "type":"publication"}
        ,{"id":"pubmed.32597660", "size":"14M", "type":"publication"}
    ]


    return obj_list



def main():

    #api_url = "https://api.glygen.org/misc/get_object/"
    api_url = "https://api.tst.glygen.org/misc/get_object/"
    ts_format = "%Y-%m-%d %H:%M:%S %Z%z"

    req_obj_list = get_req_obj_list()


    row = ["api_overhead",  "network_overhead","object_size", "object_type", "object_id"]
    print (", ".join(row))

    for req_obj in req_obj_list:
        start_ts = datetime.datetime.now(pytz.timezone('US/Eastern'))
        res = requests.post(api_url, json=req_obj, verify=False)
        end_ts = datetime.datetime.now(pytz.timezone('US/Eastern'))
        network_overhead = str(end_ts - start_ts)
        start_ts_f = start_ts.strftime(ts_format)
        end_ts_f = end_ts.strftime(ts_format)
        
        res_obj =  json.loads(res.content)

        api_overhead = res_obj["api_overhead"]["elapsed"]
        row = [api_overhead,  network_overhead,req_obj["size"], req_obj["type"], req_obj["id"]] 
        print (", ".join(row))




    return






if __name__ == '__main__':
    main()





