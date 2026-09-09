import os,sys
import string
from optparse import OptionParser
import glob
import json
from bson import json_util
import pymongo
from pymongo import MongoClient
import datetime


__version__="1.0"
__status__ = "Dev"



###############################
def main():

    doc = json.load(open("tmp/junk.json"))
    for obj in doc["results"]:
        print (obj["glytoucan_ac"])
    return




if __name__ == '__main__':
    main()
