record_type="protein"

for i in {1..10}
do
    python3 batch_api_test.py -r $record_type -b $i > logs/batch.$i.log &
done

