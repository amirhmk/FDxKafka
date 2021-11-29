import sys, os
import subprocess
sys.path.insert(0, os.getcwd())

import fd_engine.client

def handler(request):
    # subprocess.call(". setup.sh", shell=True, executable='/bin/bash')
    fd_engine.client.main(2)

if __name__ == "__main__":
    handler("")
