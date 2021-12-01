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
    start_time = time.time()
    try:
        response = requests.post(url, params=params)
    except Exception as e:
        print(f"Error for cloud function: client {i}", e)
    print("responce", response.status_code, response.text)
    end_time = time.time()
    duration = end_time - start_time
    return i, duration
    
def process_result(return_value):
    print("End Time ", time.time(), return_value)
    print(return_value)

def pool_client_map(nprocs, server_address, channel):
    # Let the executor divide the work among processes by using 'map'.
    all_results = []
    with ThreadPoolExecutor(max_workers=nprocs) as executor:
        future_to_client = {}
        for i in range(nprocs):
            future_to_client[executor.submit(create_client, i, server_address, channel)] = i
            sleep_duration = 5
            if i % 5 == 0:
                print(f"Sleeping for {sleep_duration} seconds")
                time.sleep(sleep_duration)
        # future_to_client = {executor.submit(create_client, i, server_address, channel): i for i in range(nprocs)}
        for i, future in enumerate(concurrent.futures.as_completed(future_to_client)):
            results = future_to_client[future]
            try:
                client_id, time_taken = future.result()
                print(f"time taken for client={client_id} : {round(time_taken,3)}")
                print(f"Total Completed: {i}/{nprocs}")
            except Exception as exc:
                print('%r generated an exception: %s' % (results, exc))


def run_with_gRPC(num_clients):
    """Runs the test with the default gRPC protocol"""
    GRPC_SERVER_ADDRESS = "35.203.161.106:8081"
    pool_client_map(num_clients, GRPC_SERVER_ADDRESS, 'gRPC')


def run_with_kafka(num_clients):
    """Runs the test with Kafka as communication channel"""
    KAFKA_SERVER_ADDRESS = "34.105.38.178:9091"
    pool_client_map(num_clients, KAFKA_SERVER_ADDRESS, 'kafka')


def run_test(num_clients):
    """
    Runs a training round with 1000 clients and reports:
    1. Total # of transmitted messages
    2. Total time to finish 5 rounds of training
    3. Total time for model to be updated on all devices
    """
    # Kafka
    # run_with_kafka(num_clients)
    #gRPC
    run_with_gRPC(num_clients)

if __name__ == "__main__":
    # print("Cores Available: ", mp.cpu_count())
    # pool_client(mp.cpu_count())
    run_test(200)



