import sys, os
sys.path.insert(0, os.getcwd())

import fd_engine.client

def handler(request):
    fd_engine.client.main(2)

if __name__ == "__main__":
    handler("")
