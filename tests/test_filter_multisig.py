# tests base on:
# https://prsdigg.com/articles/4375be62-6ef4-4de2-af9a-086816380fde
import os
import sys
import json
import time
import pytest
import random
import asyncio
import shlex
import signal
import shutil
import subprocess

import httpx

from pymixin.mixin_api import MixinApi
from pymixin.mixin_bot_api import MixinBotApi
from pymixin import log
from pymixin.testnet import MixinTestnet

logger = log.get_logger(__name__)

class TestFilterMultisig(object):

    @classmethod
    def setup_class(cls):
        cls.nodes = []
        # if '--newtestnet' in sys.argv:
        if True:
            for i in range(7):
                port = 7001+i
                config_dir = f'/tmp/mixin-{port}'
                if os.path.exists(config_dir):
                    shutil.rmtree(config_dir)

        if not os.path.exists('/tmp/mixin-7001'):
            cmd = f'python3 -m pymixin.main setuptestnet'
            args = shlex.split(cmd)
            p = subprocess.Popen(args, stdout=subprocess.PIPE)
            p.wait()
            logger.info('+++done!')

        for i in range(7):
            port = 7001+i
            # cmd = f'python3 -m pymixin.main kernel -dir /tmp/mixin-700{i+1} -port {port}'
            cmd = f'python3 -m pymixin.main kernel -dir /tmp/mixin-700{i+1} -port {port}'
            # cmd = f'/Users/newworld/dev/mixin/mixin/mixin kernel -dir /tmp/mixin-700{i+1} -port {port}'
            logger.info(cmd)
            args = shlex.split(cmd)
            log = open(f'/tmp/mixin-700{i+1}/log.txt', 'a')
            p = subprocess.Popen(args, stdout=log, stderr=log)
            cls.nodes.append(p)
        logger.info('++++++')
        cls.api = MixinApi('http://127.0.0.1:8001')

        loop = asyncio.get_event_loop()
        async def wait():
            api = MixinApi('http://127.0.0.1:8007')
            await asyncio.sleep(1.5)
            while True:
                try:
                    await api.get_info()
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
    async def test_filter_multisig(self):
        async def monitor():
            loop = asyncio.get_event_loop()
            reader, writer = await asyncio.open_unix_connection(path='/tmp/127.0.0.1:7001.unix', loop=loop)
            logger.info('++++++++++%s %s', reader, writer)
            while True:
                n = await reader.read(4)
                n = int.from_bytes(n, 'little')
                msg = await reader.read(n)
                logger.info(msg)
                writer.write(b'ok')
            logger.info('++++done!')
            # writer_sock.write(byte_message)
        asyncio.create_task(monitor())

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

        account2 = {
            'address': 'XINHJLCRBWJ3AgcrNhKppVMvjinapzumLVL253opKzs6Jk5bUBHWKH6paPr2exhwqYZ3FcPtbnitJMF6TXk8UcEx8u2nUt4S',
            'view_key': 'fae95f3dfaf0a7b2f4ca95d6ed94f8002492875e018000f786284be1beacf10c',
            'spend_key': '0ff0016d98026b21df80f4b1fe0db5fc460e7e66f47f67acfd773e5cc4fbb207'
        }
        logger.info("+++++++++++++++deposit++++++++++++++++++++")
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
        domain_account = {
            'view_key': view_key,
            'spend_key': signer_key
        }
        r = self.api.sign_transaction(trx, [domain_account])
        # logger.info(r)
        r = await self.api.send_raw_transaction(r['raw'])
        # logger.info(r)
        deposit_hash = r['hash']
        
        await self.api.wait_for_transaction(deposit_hash)

        input_hash = deposit_hash
        for i in range(30):
            logger.info(f"+++++++++++++++transfer++++++++++++++++++++{i}")
            trx = {
                "asset": 'a99c2e0e2b1da4d648755ef19bd95139acbbe6564cfb06dec7cd34931ca72cdc',
                "inputs": [
                    {
                    "hash": input_hash,
                    "index": 0
                    }
                ],
                "outputs": [
                    {
                    "amount": "100",
                    "accounts": [account['address']],
                    "script": "fffe01",
                    "type": 0
                    },
                ]
            }
            params = {
                "seed": '', #account['spend_key'],
                "keys": [account['view_key'] + account['spend_key']],
                "raw": trx,
                "input_index": 0
            }
            r = await self.api.get_info()

            ret = await self.api.send_transaction(trx, [account])
            input_hash = ret['hash']
            await self.api.wait_for_transaction(input_hash)
