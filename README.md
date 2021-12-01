# FDxKafka


Repository for holding our PoC for a scalable Federated Learning Implementation using Kafka

## Get Started


### Install dependencies


Dependencies are stored in a `requirements.txt` file. 
```
pip install -r requirements.txt
```

### Start the server

#### Kafka:
```
python fd_engine/server.py --numrounds 3 --broker 10.138.0.6:9092
```

#### gRPC
```
python fd_engine/server.py --grpc --numrounds 3 --broker "[::]:8080"
```

```
Usage: server.py [-h] [--broker BROKER] [--minclients MINCLIENTS]
                 [--numrounds NUMROUNDS] [--grpc]

Arguments:
  -h, --help            Show this help message and exit
  --broker BROKER       Address of server
  --minclients MINCLIENTS
                        Minimum number of clients for training
  --numrounds NUMROUNDS
                        minimum number of training rounds
  --grpc                Use gRPC as network channel. Default False
```

### Start training on the client


```
python fd_engine/cifar_numpy_test.py --broker 10.138.0.6:9092
```

## Local testing in Docker

Start local kafka and zookeeper
```
docker-compose -f kafka_cluster/docker-compose.yml up -d
```
Stop kafka
```
docker-compose -f kafka_cluster/docker-compose.yml down
```
Broker url is going to be 127.0.0.1:9091


## Evaluation


IN PROGRESS...

To deploy the current directory to GCP as a cloud function, run the following:
```
gcloud functions deploy kafkaclient --trigger-http --allow-unauthenticated --runtime python37 --entry-point handler --region us-west1
```

Entrypoint will be the `handler` function in `main.py`.

Testing parameters in JSON format are as follows:
```
{
  "broker" : "34.105.38.178:9091",
  "client_id" : "12345",
  "channel" : "kafka"
}
```

## Logs


### Connecting to kafka server through ssh
```
$ ssh bitnami@34.105.38.178
```

### Check kafka logs
```
$ less /opt/bitnami/kafka/logs/server.log
```

### Check zookeeper logs
```
$ less /opt/bitnami/zookeeper/logs/zookeeper.out
```



