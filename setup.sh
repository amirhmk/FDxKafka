
echo Adding current dir to PYTHONPATH
export PYTHONPATH=$(pwd)

echo Running Kafka Setup files...
source /home/salcainojaque/FDxKafka/kafka_consumer/setup.sh
source /home/salcainojaque/FDxKafka/kafka_producer/setup.sh

