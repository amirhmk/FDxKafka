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

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--broker", help="host_port of kafka broker")
    parser.add_argument("--minclients", help="minimum number of clients for training",
                    required=False, default=1, type=int)
    parser.add_argument("--numrounds", help="minimum number of training rounds",
                    required=False, default=3, type=int)
    parser.add_argument("--grpc", help="Use gRPC as Network Channel. Default False",
                    required=False, default=False, action='store_true')
    args = parser.parse_args()
    print(args)
    fl.server.start_server(server_address=args.broker, 
                        config={"num_rounds": args.numrounds, "min_fit_clients" : args.minclients,
                                "use_kafka" : not args.grpc})
