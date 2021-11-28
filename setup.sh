
echo Adding current dir to PYTHONPATH
export PYTHONPATH=$(pwd)

echo Running Kafka Setup files...

source kafka_producer/setup.sh

