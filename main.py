import sys, os
import time
sys.path.insert(0, os.getcwd())

import fd_engine.client
# import fd_engine.cifar_numpy_test

def handler(request):
    start_time = time.time()
    # subprocess.call(". setup.sh", shell=True, executable='/bin/bash')
    broker = "34.105.38.178:9091"
    if request is not None and request.broker is not None:
        broker = request.broker
        print(f"Using request broker: {request.broker}")
    
    if request.client_id is None:
        clientid = None    
    else:
        clientid = request.client_id

    print(f"Starting request for client id {clientid}")
    fd_engine.client.main(clientid,broker)
    # fd_engine.cifar_numpy_test.main(broker)
    end_time = time.time()
    duration = f"{end_time - start_time} Sec"
    print("Duration: ", duration)
    return duration

if __name__ == "__main__":
    handler("")
