import sys, os
import time
sys.path.insert(0, os.getcwd())

import fd_engine.client

def handler(request):
    request_json = request.get_json(silent=True)
    request_args = request.args
    print("request_json", request_json)

    if request_json and 'broker' in request_json:
        broker = request_json['broker']
        client_id = request_json['client_id']
        channel = request_json['channel']
    elif request_args and 'broker' in request_args:
        broker = request_args['broker']
        client_id = request_args['client_id']
        channel = request_args['channel']
    else:
        broker = "34.105.38.178:9091"
        client_id = 3
        channel = 'kafka'

    print(f"request broker: {broker}")
    start_time = time.time()
    fd_engine.client.main(client_id, broker=broker, channel=channel)
    end_time = time.time()
    duration = end_time - start_time
    print(f"Duration: {duration} Sec")
    return duration

if __name__ == "__main__":
    handler("")
