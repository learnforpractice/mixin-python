import sys
import json
from . import _mixin

if __name__ == '__main__':
    args = json.dumps(sys.argv)
    _mixin.main(args)
