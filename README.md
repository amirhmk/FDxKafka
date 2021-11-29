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
Usage: server.py [-h] [--broker BROKER] [--minclients MINCLIENTS]
                 [--numrounds NUMROUNDS]

```
Optional arguments:
  -h, --help      show this help message and exit
  --broker        host:port of kafka broker
  --minclients    minimum number of clients for training
  --numrounds     minimum number of training rounds
```

### Start training on the client


```
python fd_engine/cifar_numpy_test.py --broker 10.138.0.6:9092
```


## Evaluation


IN PROGRESS...

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



