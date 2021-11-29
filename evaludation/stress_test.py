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
import fd_engine.client
import multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor


def worker_process(i):
    print("Start Time", time.time(), i * i)
    fd_engine.client.main(i)
    return i * i # square the argument
    
def process_result(return_value):
    print("End Time ", time.time(), return_value)
    print(return_value)

def pool_client_map(nums, nprocs):
    # Let the executor divide the work among processes by using 'map'.
    with ProcessPoolExecutor(max_workers=nprocs) as executor:
        return {num:factors for num, factors in
                                zip(nums,
                                    executor.map(worker_process, nums))}

def pool_client(nprocs):
    pool = mp.Pool()
    for i in range(nprocs):
        pool.apply_async(worker_process, args=(i,), callback=process_result)
    pool.close()
    pool.join()

def spin_up_instances():
    """Spins up 1000 instances"""
    pass


def run_with_gRPC():
    """Runs the test with the default gRPC protocol"""
    pass


def run_with_kafka():
    """Runs the test with Kafka as communication channel"""
    pass


def run_test():
    """
    Runs a training round with 1000 clients and reports:
    1. Total # of transmitted messages
    2. Total time to finish 5 rounds of training
    3. Total time for model to be updated on all devices
    """

    pass


if __name__ == "__main__":
    print("Cores Available: ", mp.cpu_count())
    pool_client(mp.cpu_count())



