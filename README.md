# FDxKafka
Repository for holding our PoC for a scalable Federated Learning Implementation using Kafka


# Connecting to kafka server through ssh
```
$ ssh bitnami@34.105.38.178
```

# Check kafka logs
```
$ less /opt/bitnami/kafka/logs/server.log
```

# Check zookeeper logs
```
$ less /opt/bitnami/zookeeper/logs/zookeeper.out
```


# Flower Federated Learning over Kafka

## start the server
```
python fd_engine/server.py --broker 10.138.0.6:9092 --numrounds 3
```
Usage: server.py [-h] [--broker BROKER] [--minclients MINCLIENTS]
                 [--numrounds NUMROUNDS]

Optional arguments:
  -h, --help            show this help message and exit
  --broker BROKER       host:port of kafka broker
  --minclients MINCLIENTS
                        minimum number of clients for training
  --numrounds NUMROUNDS
                        minimum number of training rounds

## start the training on the client
```
python fd_engine/cifar_numpy_test.py --broker 10.138.0.6:9092
```



