import sys, os
import subprocess
sys.path.insert(0, os.getcwd())

import fd_engine.client

def handler(request):
    # subprocess.call(". setup.sh", shell=True, executable='/bin/bash')
    broker = None
    if request.broker is not None:
      broker = request.broker
    fd_engine.client.main(2, broker)

if __name__ == "__main__":
    handler("")
