"""
Scrip to run evaludation of Kafka vs gRPC
https://stackoverflow.com/questions/20039659/python-multiprocessings-pool-process-limit
processes vs threads?
How many processes to spin up?

Idea:
Setup Cloud functions where each client is a single invokation.
As a responce, get the total time for each client.

Problem:
How do we get the source code?

Serverless isn't gonna work, package sizes are too big.

EKS may be our best bet. Will try making this work for 2 processes, then move on to more.

"""
import time
import requests
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor


def create_client(i, server_address, channel):
    url = "https://us-west1-manifest-design-328217.cloudfunctions.net/kafkaclient"
    params = {
        "broker": server_address,
        "client_id": i,
        "channel": channel
        }
    print(f"Called cloud function {i}")
    response = requests.post(url, params=params)
    print(response)
    return i * i # square the argument
    
def process_result(return_value):
    print("End Time ", time.time(), return_value)
    print(return_value)

def pool_client_map(nprocs, server_address, channel):
    # Let the executor divide the work among processes by using 'map'.
    all_results = []
    with ThreadPoolExecutor(max_workers=nprocs) as executor:
        future_to_client = {executor.submit(create_client, i, server_address, channel): i for i in range(nprocs)}
        for future in concurrent.futures.as_completed(future_to_client):
            results = future_to_client[future]
        try:
            data = future.result()
            print("data", data)
        except Exception as exc:
            print('%r generated an exception: %s' % (results, exc))
        else:
            print('%r page is %d bytes' % (results, len(data)))


def spin_up_instances():
    """Spins up 1000 instances"""
    pass


def run_with_gRPC():
    """Runs the test with the default gRPC protocol"""
    GRPC_SERVER_ADDRESS = "34.105.38.178:8080"
    pool_client_map(3, GRPC_SERVER_ADDRESS, 'gRPC')


def run_with_kafka():
    """Runs the test with Kafka as communication channel"""
    KAFKA_SERVER_ADDRESS = "34.105.38.178:9091"
    pool_client_map(3, KAFKA_SERVER_ADDRESS, 'kafka')


def run_test():
    """
    Runs a training round with 1000 clients and reports:
    1. Total # of transmitted messages
    2. Total time to finish 5 rounds of training
    3. Total time for model to be updated on all devices
    """
    # Kafka
    run_with_kafka()
    #gRPC
    run_with_gRPC()

if __name__ == "__main__":
    # print("Cores Available: ", mp.cpu_count())
    # pool_client(mp.cpu_count())
    pool_client_map(3)



