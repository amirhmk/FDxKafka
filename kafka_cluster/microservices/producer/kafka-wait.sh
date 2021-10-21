#!/bin/bash

test="${KAFKA_BROKER_URL/:/ }"

cmd=`nc -w 2 -vz $test`
while [[ $? -eq 1 ]] ; do 
    echo $(date) " Waiting for Kafka listener state at $test"
    sleep 5
    cmd=`nc -w 2 -vz $test`
done

echo $(date) " Launching Finnhub worker"

python finnancial_data_producer.py