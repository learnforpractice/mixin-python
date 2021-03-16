import os
import json
import time
import pytest
import ctypes
import logging
import uuid
import base64
import gzip
import random
import asyncio
import threading
import shlex
import signal
import subprocess
from io import BytesIO

import httpx

from mixin.mixin_api import MixinApi
from mixin.mixin_bot_api import MixinBotApi
from mixin import mixin_config
from mixin import log
from mixin.testnet import MixinTestnet

logger = log.get_logger(__name__)

class TestMixinApi(object):

    @classmethod
    def setup_class(cls):
        cls.nodes = []
        if not os.path.exists('/tmp/mixin-7001'):
            cmd = f'python3 -m mixin.main setuptestnet'
            args = shlex.split(cmd)
            p = subprocess.Popen(args, stdout=subprocess.PIPE)
            p.wait()
            logger.info('+++done!')

        for i in range(7):
            port = 7001+i
            cmd = f'python3 -m mixin.main kernel -dir /tmp/mixin-700{i+1} -port {port}'
            logger.info(cmd)
            args = shlex.split(cmd)
            p = subprocess.Popen(args, stdout=subprocess.PIPE)
            cls.nodes.append(p)
        logger.info('++++++')
        cls.api = MixinApi('http://127.0.0.1:8001')

        loop = asyncio.get_event_loop()        
        async def wait():
            api = MixinApi('http://127.0.0.1:8007')
            await asyncio.sleep(0.5)
            while True:
                try:
                    await cls.api.get_info()
                    return
                except Exception as e:
                    await asyncio.sleep(0.5)
                    logger.info(e)
        loop.run_until_complete(wait())
        logger.info("++++setup_class return")

    @classmethod
    def teardown_class(cls):
        for p in cls.nodes:
            p.send_signal(signal.SIGINT)
            p.wait()

    def setup_method(self, method):
        logger.warning('test start: %s', method.__name__)

    def teardown_method(self, method):
        pass

    @pytest.mark.asyncio
    async def test_hello(self):
        if self.auto_start_testnet:
            logger.info(self.testnet.config_dirs)
        await asyncio.sleep(1.0)
        info = await self.api.get_info()
        # for key in info:
        #     print(key)
        logger.info('+++epoch: %s', info['epoch'])
        logger.info('+++mint: %s', info['mint'])
        logger.info('+++network: %s', info['network'])
        logger.info('+++node: %s', info['node'])
        logger.info('+++queue: %s', info['queue'])
        logger.info('+++timestamp: %s', info['timestamp'])
        logger.info('+++uptime: %s', info['uptime'])
        logger.info('+++version: %s', info['version'])
        return
        logger.info(json.dumps(info, indent=' '))


    @pytest.mark.asyncio
    async def test_deposit(self):
        with open('/tmp/mixin-7001/config.toml', 'r') as f:
            for line in f:
                key = 'signer-key = '
                start = line.find(key)
                if start >= 0:
                    signer_key = line[len(key):]
                    signer_key = signer_key.strip()
                    signer_key = signer_key.replace('"', '')
                    break

        logger.info('++++signer_key: %s', signer_key)
        with open('/tmp/mixin-7001/nodes.json', 'r') as f:
            nodes = f.read()
            nodes = json.loads(nodes)
            domain_node = nodes[0]
        logger.info(domain_node)
        domain_address = domain_node['signer']
        decoded_addr = self.api.decode_address(domain_address)
        view_key = decoded_addr['private_spend_key_derive']
        view_key = view_key.strip()
        logger.info('+++++view key: %s', view_key)

        account = {
            'address': 'XINFrqT5x74BVvtgLJEVhRhFc1GdJ3vmwiu7zJHVg7qjYvzx9wG7j1sENkXV7NfN9tQm1SsRNces7tcrxFas9nkr5H1B7HTm',
            'view_key': 'bd1a337f2319d502eb062a433cb79cf8e2daadd6bcd0bb2a21d4b073549cb30c',
            'spend_key': 'bd449970bdb5cf9afaf1f9c574a94f06ff7a0d3af0d9387867e1ba7e9193eb03'
        }

        trx = {
            "asset": "a99c2e0e2b1da4d648755ef19bd95139acbbe6564cfb06dec7cd34931ca72cdc",
            "inputs": [{
                "deposit": {
                "chain": "8dd50817c082cdcdd6f167514928767a4b52426997bd6d4930eca101c5ff8a27",
                "asset": "0xa974c709cfb4566686553a20790685a47aceaa33",
                "transaction": "0x4cb581281f7115706c5e6f669371574bfdea317325e15eef32cd356df0d4789b",
                "index": 0,
                "amount": "100"
                }
            }],
            "outputs": [
                {
                "amount": "100",
                "accounts": [account['address']],
                "script": "fffe01",
                "type": 0
                }
            ]
        }
        logger.info(trx)
        logger.info(view_key + signer_key)
        # sign transaction with doman signer key
        params = {
            "seed": '', #account['spend_key'],
            "key": json.dumps([view_key + signer_key,]),
            "raw": json.dumps(trx),
            "inputIndex": "0"
        }
        r = self.api.sign_transaction(params)
        logger.info(r)
        r = await self.api.send_transaction(r['raw'])
        logger.info(r)

        await asyncio.sleep(3.0)
        r = await self.api.get_transaction(r['hash'])
        logger.info(r)

'''
./src/mixin/mixin kernel -dir ./testnet/config-7001 -port 7001
./src/mixin/mixin kernel -dir ./testnet/config-7002 -port 7002
./src/mixin/mixin kernel -dir ./testnet/config-7003 -port 7003
./src/mixin/mixin kernel -dir ./testnet/config-7004 -port 7004
./src/mixin/mixin kernel -dir ./testnet/config-7005 -port 7005
./src/mixin/mixin kernel -dir ./testnet/config-7006 -port 7006
./src/mixin/mixin kernel -dir ./testnet/config-7007 -port 7007
'''
