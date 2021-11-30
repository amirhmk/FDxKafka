import sys, os
import time
sys.path.insert(0, os.getcwd())

import fd_engine.client
import fd_engine.cifar_numpy_test

def handler(request):
    start_time = time.time()
    # subprocess.call(". setup.sh", shell=True, executable='/bin/bash')
    # fd_engine.client.main(2)
    kafka_server = "10.138.0.6:9092"
    fd_engine.cifar_numpy_test.main(kafka_server)
    end_time = time.time()
    duration = f"{end_time - start_time} Sec"
    print("Duration: ", duration)
    return duration

if __name__ == "__main__":
    handler("")
