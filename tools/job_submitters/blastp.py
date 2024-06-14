import sys
import subprocess


def main():

    try:
        cmd = "/app/ncbi-blast-2.6.0+/bin/blastp"
        for v in sys.argv[1:]:
            cmd += " %s" % (v)
        x,y = subprocess.getstatusoutput(cmd)
        if x != 0:
            err = y.split("\n")[0]
            print (err)
            exit(1)
    except Exception as err:
        print (err)



if __name__ == '__main__':
    main()


