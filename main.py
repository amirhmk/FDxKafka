import sys, os
import time
sys.path.insert(0, os.getcwd())

import fd_engine.client
import fd_engine.cifar_numpy_test

def handler(request):
    start_time = time.time()
    # subprocess.call(". setup.sh", shell=True, executable='/bin/bash')
    broker = "10.138.0.6:9092"
    if request.broker is not None:
      broker = request.broker
    
    fd_engine.cifar_numpy_test.main(broker)
    end_time = time.time()
    duration = f"{end_time - start_time} Sec"
    print("Duration: ", duration)
    return duration

if __name__ == "__main__":
    handler("")
