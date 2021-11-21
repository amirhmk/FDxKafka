#!/bin/bash

test="${KAFKA_BROKER_URL/:/ }"

cmd=`nc -w 2 -vz $test`
while [[ $? -eq 1 ]] ; do 
    echo $(date) " Waiting for Kafka listener state at $test"
    sleep 5
    cmd=`nc -w 2 -vz $test`
done

echo $(date) " Launching twitter classifier worker"

python3 python/consumer.py &

sleep infinity
