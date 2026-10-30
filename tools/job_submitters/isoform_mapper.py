import sys
import subprocess
from optparse import OptionParser
import json


def main():

    usage = "\n%prog  [options]"
    parser = OptionParser(usage,version="%prog version___")
    parser.add_option("-a","--afile",action="store",dest="afile",help="")

    (options,args) = parser.parse_args()
    for key in ([options.afile]):
        if not (key):
            parser.print_help()
            sys.exit(0)
   
    a_file = options.afile
    doc = json.load(open(a_file))
  
    in_file = doc[0]["-i"]
    in_dir = in_file.replace("/input.csv", "")
    
    try:
        cmd = "docker run --rm -v %s:/input ebiglygen/mapper-java-jar:basic" % (in_dir)
        x,y = subprocess.getstatusoutput(cmd)
        #if x != 0:
        #    err = y.split("\n")[0]
        #    print (err)
        #    exit(1)
    except Exception as err:
        print (err)



if __name__ == '__main__':
    main()


