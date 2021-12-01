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
python fd_engine/server.py --numrounds 5 --broker 10.138.0.6:9092
```

#### gRPC
```
python fd_engine/server.py --grpc --numrounds 5 --broker "[::]:8080"
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
python fd_engine/client.py --broker 10.138.0.6:9092
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

Read kafka server logs

```
docker logs broker -f
```


## Evaluation

In order to compare our implementation, we use the existing gRPC channel as the benchmark. Then we perform the following:

1. Spin up a server:
   1. 5 training rounds
   2. 100 minimum devices
2. Spin up clients in the following way:
   1. Spin up 50 clients using cloud function
   2. Spin up 50 clients using local setup, and GCP instances

In our evaluation, we measure the following for each of `gRPC` and `kafka` channels:
1. Total # of transmitted messages
2. Total time to finish 5 rounds of training
3. Total time for model to be updated on all devices


### Running evaluations

1. Start up the server as outlined above. 
2. Spin up the cloud function clients: (Make sure you're in `evaluations` directory: `npm test`
3. From the root directory, run `python evaluations/stress_test.py`
  This terminal window will report the above metrics.

### Results

#### gRPC
```
Total time: FL finished in 178.52631062400178
Training start time: 22:35:15,361
Training end time: 22:35:28
Total training time: 13s
```

#### Kafka

```
Total time: FL finished in ?
Training start time: ?
Training end time: ?
Total training time: ?
```

### Cloud functions

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



