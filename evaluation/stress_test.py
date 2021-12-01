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
from concurrent.futures import thread
import sys, os
sys.path.insert(0, os.getcwd())
import time
import requests
import concurrent.futures
import multiprocessing as mp
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

import fd_engine.client

import numpy as np


def create_local_client(i, server_address, channel):
    print(f"Created local client {i}")
    start_time = time.time()
    fd_engine.client.main(client_id=i, broker=server_address, channel=channel)
    end_time = time.time()
    duration = end_time - start_time
    return i, duration

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
        response = requests.get(url, params=params)
    except Exception as e:
        print(f"Error for cloud function: client {i}", e)
    print("responce", i, response.status_code, response.text)
    end_time = time.time()
    duration = end_time - start_time
    return i, duration
    
def pool_client_local(nprocs, server_address, channel):
    all_results = []
    with ProcessPoolExecutor(max_workers=nprocs) as executor:
        future_to_client = {executor.submit(create_local_client, i, server_address, channel): i for i in range(1, nprocs+1)}
        for i, future in enumerate(concurrent.futures.as_completed(future_to_client)):
            results = future_to_client[future]
            try:
                client_id, time_taken = future.result()
                print(f"time taken for client={client_id} : {round(time_taken,3)}")
                all_results.append(time_taken)
                print(f"Total Completed: {i}/{nprocs}")
            except Exception as exc:
                print('%r generated an exception: %s' % (results, exc))
    return np.average(all_results)


def pool_client_cloud_function(nprocs, server_address, channel):
    # Let the executor divide the work among processes by using 'map'.
    all_results = []
    print("HeLLLLO")
    with ThreadPoolExecutor(max_workers=nprocs) as executor:
        future_to_client = {}
        for i in range(1, nprocs+1):
            future_to_client[executor.submit(create_client, i, server_address, channel)] = i
            sleep_duration = 2
            if i % 5 == 0:
                print(f"Sleeping for {sleep_duration} seconds")
                time.sleep(sleep_duration)
        for i, future in enumerate(concurrent.futures.as_completed(future_to_client)):
            results = future_to_client[future]
            try:
                client_id, time_taken = future.result()
                print(f"time taken for client={client_id} : {round(time_taken,3)}")
                print(f"Total Completed: {i}/{nprocs}")
                all_results.append(time_taken)
            except Exception as exc:
                print('%r generated an exception: %s' % (results, exc))
    return np.average(all_results)


def run_with_gRPC(num_clients):
    """Runs the test with the default gRPC protocol"""
    GRPC_SERVER_ADDRESS = "35.203.161.106:8081"
    with ThreadPoolExecutor(max_workers=2) as executor:
        future_to_client = {}
        # future_to_client[executor.submit(pool_client_cloud_function, 5, GRPC_SERVER_ADDRESS, 'gRPC')] = "CLOUD_FUNCTION"
        future_to_client[executor.submit(pool_client_local, 8, GRPC_SERVER_ADDRESS, 'gRPC')] = "LOCAL"
        for i, future in enumerate(concurrent.futures.as_completed(future_to_client)):
            results = future_to_client[future]
            try:
                average_time = future.result()
                print(f"Average Time {results}", average_time)
            except Exception as exc:
                print('%r generated an exception: %s' % (results, exc))



def run_with_kafka(num_clients):
    """Runs the test with Kafka as communication channel"""
    KAFKA_SERVER_ADDRESS = "34.105.38.178:9091"
    pool_client_cloud_function(num_clients, KAFKA_SERVER_ADDRESS, 'kafka')


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
    print("Cores Available: ", mp.cpu_count())
    # pool_client_local(mp.cpu_count())
    run_test(mp.cpu_count())
    # run_test(20)



