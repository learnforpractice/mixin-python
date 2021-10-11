import time
import shlex
import subprocess
from pymixin import log

logger = log.get_logger(__name__)
logger.addHandler(log.handler)

cmd = 'python3.7 -m pymixin.main kernel -dir ../mixin/config'
#cmd = 'ls -l'

log = open(f'mixin.log', 'a')

while True:
    args = shlex.split(cmd)
    try:
        p = subprocess.Popen(args, stdout=log, stderr=log)
        r = p.wait()
        logger.warning('%s return %s', cmd, r)
        time.sleep(1.0)
    except Exception as e:
        logger.warning(e)
