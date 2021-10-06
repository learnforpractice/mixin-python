import sys
import json
import threading
import signal
import sys

from . import _mixin

def signal_handler(sig, frame):
    print('exiting...')
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def main():
    sys.argv[0] = 'mixin'
    args = json.dumps(sys.argv)
    def start():
        _mixin.main(args)
    t = threading.Thread(target=start, daemon=True)
    t.start()
    t.join()

if __name__ == '__main__':
    main()