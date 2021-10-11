import os
import json
import time
import asyncio
import shlex
import subprocess

import httpx

from pymixin.mixin_api import MixinApi
from pymixin import log
from pymixin.testnet import MixinTestnet

logger = log.get_logger(__name__)


nodes = []

if not os.path.exists('/tmp/mixin-7001'):
    cmd = f'python3 -m pymixin.main setuptestnet'
    args = shlex.split(cmd)
    p = subprocess.Popen(args, stdout=subprocess.PIPE)
    p.wait()

for i in range(7):
    port = 7001+i
    cmd = f'python3 -m pymixin.main kernel -dir /tmp/mixin-700{i+1} -port {port}'
    logger.info(cmd)
    args = shlex.split(cmd)
    p = subprocess.Popen(args, stdout=subprocess.PIPE)
    nodes.append(p)

time.sleep(2.0)

api = MixinApi('http://127.0.0.1:8001')

async def start():
    while True:
        for i in range(7):
            url = f'http://127.0.0.1:800{i+1}'
            api.set_node(url)
            try:
                await api.get_info()
            except Exception as e:
                print(e)
                print(f'++++++++node {i+1} down')
        time.sleep(3.0)

loop = asyncio.get_event_loop()
loop.run_until_complete(start())
