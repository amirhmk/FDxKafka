import sys, os
import time
sys.path.insert(0, os.getcwd())

import fd_engine.client

def handler(request):
    start_time = time.time()
    request_json = request.get_json(silent=True)
    request_args = request.args
    print("request_json", request_json)

    if request_json and 'broker' in request_json:
        broker = request_json['broker']
    elif request_args and 'broker' in request_args:
        broker = request_args['broker']
    else:
        broker = "34.105.38.178:9091"
    print(f"request broker: {broker}")
    fd_engine.client.main(2, broker)
    # fd_engine.cifar_numpy_test.main(broker)
    end_time = time.time()
    duration = end_time - start_time
    print(f"Duration: {duration} Sec")
    return duration

if __name__ == "__main__":
    handler("")
