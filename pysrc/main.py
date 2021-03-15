import sys
import json
import threading
import signal
import sys

from . import _mixin

def signal_handler(sig, frame):
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

if __name__ == '__main__':
    args = json.dumps(sys.argv)
    def start():
        _mixin.main(args)
    t = threading.Thread(target=start)
    t.start()
    t.join()
