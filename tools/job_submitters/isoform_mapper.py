import sys
import subprocess
from optparse import OptionParser



def main():

    usage = "\n%prog  [options]"
    parser = OptionParser(usage,version="%prog version___")
    parser.add_option("-i","--infile",action="store",dest="infile",help="Input file")

    (options,args) = parser.parse_args()
    for key in ([options.infile]):
        if not (key):
            parser.print_help()
            sys.exit(0)
    
    in_file = options.infile
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


