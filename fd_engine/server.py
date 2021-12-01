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
    parser.add_argument("--grpc", help="Use gRPC as Network Channel. Default False",
                    required=False, default=False, action='store_true')
    
    parser.add_argument("--numrounds", help="minimum number of training rounds",
                    required=False, default=3, type=int)
    parser.add_argument("--minclients", help=" Minimum number of clients used during training. Defaults to 2.",
                    required=False, default=2, type=int)
    parser.add_argument("--min_eval_clients", help="Minimum number of clients used during validation. Defaults to 2.",
                    required=False, default=2, type=int)
    parser.add_argument("--min_available_clients", help="Minimum number of total clients in the system. Defaults to 2.",
                    required=False, default=2, type=int)

    args = parser.parse_args()
    print(args)
    try:
        fl.server.start_server(server_address=args.broker,
                            use_kafka=not args.grpc,
                            config={"num_rounds": args.numrounds, 
                                    "min_fit_clients" : args.minclients,
                                    "min_eval_clients" : args.min_eval_clients,
                                    "min_available_clients" : args.min_available_clients,
                                })
    except:
        print("Server stopped.")
        sys.exit()