server="tst"
grp_list="protein glycan site motif publication biomarker supersearch globalsearch usecases"

for grp in $grp_list
do
    python3 test_performance.py -s $server -g $grp
done

