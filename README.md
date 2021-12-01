# FDxKafka


Repository for holding our PoC for a scalable Federated Learning Implementation using Kafka

## Get Started


### Install dependencies


Dependencies are stored in a `requirements.txt` file. 
```
pip install -r requirements.txt
```

### Start the server

```
python fd_engine/server.py --broker 10.138.0.6:9092 --numrounds 3
```

```
Usage: server.py [-h] [--broker BROKER] [--minclients MINCLIENTS]
                 [--numrounds NUMROUNDS] [--grpc]

Arguments:
  -h, --help            show this help message and exit
  --broker BROKER       host_port of kafka broker
  --minclients MINCLIENTS
                        minimum number of clients for training
  --numrounds NUMROUNDS
                        minimum number of training rounds
  --grpc                Use gRPC as Network Channel. Default False


```

### Start training on the client


```
python fd_engine/cifar_numpy_test.py --broker 10.138.0.6:9092
```


## Evaluation


IN PROGRESS...

To deploy the current directory to GCP as a cloud function, run the following:
```
gcloud functions deploy kafkaclient --trigger-http --allow-unauthenticated --runtime python37 --entry-point handler --region us-west1
```

Entrypoint will be the `handler` function in `main.py`.

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



