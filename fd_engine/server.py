import flwr as fl

fl.server.start_server("0.0.0.0:8081", config={"num_rounds": 3})

