import commands

#this python script is wrapper for matlab script

cmd = "/usr/local/bin/matlab -nodisplay -nojvm -nosplash -nodesktop -r \"run('hello.m')\""
cmd = "cat /tmp/junk.csv"
output = commands.getoutput(cmd)

print output

