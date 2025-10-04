import sys
import subprocess


def main():

    try:
        cmd = "docker exec -t running_glygen_retriever python /app/retriever.py"
        for v in sys.argv[1:]:
            cmd += " %s" % (v)
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


