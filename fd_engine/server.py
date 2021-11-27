import flwr as fl

fl.server.start_server("kafka-vm-1:9092", config={"num_rounds": 3})

