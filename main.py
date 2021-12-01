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

    # subprocess.call(". setup.sh", shell=True, executable='/bin/bash')
    print(f"Starting request for client id {client_id}")
    # fd_engine.cifar_numpy_test.main(broker)
    fd_engine.client.main(client_id=client_id, broker=broker, channel=channel)
    return

if __name__ == "__main__":
    handler("")
