import sys, os
sys.path.insert(0, os.getcwd())
import yaml
import flwr as fl
import argparse

cfg = os.path.join(os.getcwd(), 'env.yaml')
with open(cfg, 'r') as f:
    configparam = yaml.load(f,Loader=yaml.FullLoader)

os.environ['KAFKA_USERNAME'] = configparam['config']['KAFKA_USERNAME']
os.environ['KAFKA_PASSWORD'] = configparam['config']['KAFKA_PASSWORD']

a = argparse.ArgumentParser()
a.add_argument("--broker", help="host_port of kafka broker")
a.add_argument("--minclients", help="minimum number of clients for training",
                required=False, default=1, type=int)
args = a.parse_args()
print(args)
fl.server.start_server(server_address=args.broker, config={"num_rounds": 3, "min_fit_clients" : args.minclients})
