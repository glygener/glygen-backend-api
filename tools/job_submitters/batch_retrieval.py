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
    out_file = doc[1]["-o"]
    rel = doc[2]["-r"]


    try:
        cmd = "docker exec -t running_glygen_retriever python /app/retriever.py"
        cmd += " -i %s -o %s -r %s" % (in_file, out_file, rel)
        x,y = subprocess.getstatusoutput(cmd)
        #print ("flag-A", x, y)
        if x != 0:
            err = "; ".join(y.split("\n"))
            print (err)
            exit(-1)
    except Exception as err:
        print (err)
        exit(-1)


if __name__ == '__main__':
    main()


