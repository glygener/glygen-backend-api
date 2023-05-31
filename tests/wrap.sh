server="beta"
record_type="protein"


for i in {1..10}
do
    python3 batch_api_test.py -s $server -r $record_type -b $i > logs/batch.$i.log &
done

