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

class TestMixinApi(object):

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
            # cmd = f'python3 -m mixin.main kernel -dir /tmp/mixin-700{i+1} -port {port}'
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
        with open('/tmp/mixin-7001/genesis.json', 'r') as f:
            genesis = f.read()
            genesis = json.loads(genesis)
            domain_node = genesis['domains'][0]
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
        logger.info(self.api.decode_transaction(r['raw']))
        r = await self.api.send_raw_transaction(r['raw'])
        # logger.info(r)
        deposit_hash = r['hash']

        await self.wait_for_transaction(deposit_hash)

        logger.info("+++++++++++++++transfer++++++++++++++++++++")
        trx = {
            "asset": 'a99c2e0e2b1da4d648755ef19bd95139acbbe6564cfb06dec7cd34931ca72cdc',
            "inputs": [
                {
                "hash": deposit_hash,
                "index": 0
                }
            ],
            "outputs": [
                {
                "amount": "51",
                "accounts": [account['address']],
                "script": "fffe01",
                "type": 0
                },
                {
                "amount": "49",
                "accounts": [account2['address']],
                "script": "fffe01",
                "type": 0
                }
            ]
        }

        # logger.info(trx)
        params = {
            "seed": '', #account['spend_key'],
            "keys": [account['view_key'] + account['spend_key']],
            "raw": trx,
            "input_index": 0
        }
        r = await self.api.get_info()

        trx_hash = await self.send_transaction(trx, [account])

        logger.info("+++++++++++++++withdraw++++++++++++++++++++")
        trx = {
            "asset": "a99c2e0e2b1da4d648755ef19bd95139acbbe6564cfb06dec7cd34931ca72cdc",
            "extra": b"hello,world".hex(),
            "inputs": [
                {
                "hash": trx_hash,
                "index": 0
                }
            ],
            "outputs": [
                {
                "amount": "50",
                "withdrawal": {
                    "chain": "8dd50817c082cdcdd6f167514928767a4b52426997bd6d4930eca101c5ff8a27",
                    "asset_key": "0xa974c709cfb4566686553a20790685a47aceaa33",
                    "address": "0x62E2110D4F76e15Ae40FE1e139f249a1F1afd8b5",
                    "tag":"hello,world"
                },
                "type": 161
                },
                {
                "amount": "1",
                "accounts": [
                    account2['address']
                ],
                "script": "fffe01",
                "type": 0
                }
            ]
        }

        params = {
            "seed": '', #account['spend_key'],
            "keys": [account['view_key'] + account['spend_key']],
            "raw": trx,
            "input_index": 0
        }
        await self.send_transaction(trx, [account])

    @pytest.mark.asyncio
    async def test_transfer_with_multiple_input(self):

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
        with open('/tmp/mixin-7001/genesis.json', 'r') as f:
            genesis = f.read()
            genesis = json.loads(genesis)
            domain_node = genesis['domains'][0]
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
        
        await self.wait_for_transaction(deposit_hash)

        trx = {
            "asset": "a99c2e0e2b1da4d648755ef19bd95139acbbe6564cfb06dec7cd34931ca72cdc",
            "inputs": [
                {
                "hash": deposit_hash,
                "index": 0
                }
            ],
            "outputs": [
                {
                "amount": "51",
                "accounts": [account['address']],
                "script": "fffe01",
                "type": 0
                },
                {
                "amount": "49",
                "accounts": [account['address']],
                "script": "fffe01",
                "type": 0
                }
            ]
        }
        r = await self.api.send_transaction(trx, [account])
        await self.api.wait_for_transaction(r['hash'])

        trx_hash = r['hash']

        trx = {
            "asset": "a99c2e0e2b1da4d648755ef19bd95139acbbe6564cfb06dec7cd34931ca72cdc",
            "inputs": [
                {
                "hash": trx_hash,
                "index": 0
                },
                {
                "hash": trx_hash,
                "index": 1
                }
            ],
            "outputs": [
                {
                "amount": "100",
                "accounts": [account['address']],
                "script": "fffe01",
                "type": 0
                }
            ]
        }
        r = await self.api.send_transaction(trx, [account])
        r = await self.api.wait_for_transaction(r['hash'])
        logger.info(r)

    @pytest.mark.asyncio
    async def test_transfer_with_multiple_input_with_different_keys(self):

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
        with open('/tmp/mixin-7001/genesis.json', 'r') as f:
            genesis = f.read()
            genesis = json.loads(genesis)
            domain_node = genesis['domains'][0]
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
        
        await self.wait_for_transaction(deposit_hash)

        trx = {
            "asset": "a99c2e0e2b1da4d648755ef19bd95139acbbe6564cfb06dec7cd34931ca72cdc",
            "inputs": [
                {
                "hash": deposit_hash,
                "index": 0
                }
            ],
            "outputs": [
                {
                "amount": "51",
                "accounts": [account['address']],
                "script": "fffe01",
                "type": 0
                },
                {
                "amount": "49",
                "accounts": [account2['address']],
                "script": "fffe01",
                "type": 0
                }
            ]
        }
        r = await self.api.send_transaction(trx, [account])
        await self.api.wait_for_transaction(r['hash'])

        trx_hash = r['hash']

        trx = {
            "asset": "a99c2e0e2b1da4d648755ef19bd95139acbbe6564cfb06dec7cd34931ca72cdc",
            "inputs": [
                {
                "hash": trx_hash,
                "index": 0
                },
                {
                "hash": trx_hash,
                "index": 1
                }
            ],
            "outputs": [
                {
                "amount": "100",
                "accounts": [account['address']],
                "script": "fffe01",
                "type": 0
                }
            ]
        }

        signatures = []
        seed = self.api.generate_random_seed()
        logger.info(seed)
        r = self.api.sign_transaction(trx, [account], [0], seed=seed)
        signatures.append(r['signatures'][0])

        r = self.api.sign_transaction(trx, [account2], [1], seed=seed)
        signatures.append(r['signatures'][0])

        raw = self.api.add_signatures_to_raw_transaction(r['raw'], signatures)
        r = self.api.decode_transaction(raw)
        logger.info(r)
        r = await self.api.send_raw_transaction(raw)
        r = await self.api.wait_for_transaction(r['hash'])
        logger.info(r)

    @pytest.mark.asyncio
    async def test_get_info(self):
        r = await self.api.get_info()
        logger.info(r)

    @pytest.mark.asyncio
    async def test_list_all_nodes(self):
        info = await self.api.list_all_nodes(0, True)
        logger.info(info)

    @pytest.mark.asyncio
    async def test_get_utxo(self):
        info = await self.api.list_all_nodes(0, True)
        logger.info(info)
        hash = info[0]['transaction']
        utxo = await self.api.get_utxo(hash, 0)
        logger.info(utxo)

    @pytest.mark.asyncio
    async def test_get_snapshot(self):
        info = await self.api.list_all_nodes(0, True)
        logger.info(info)
        hash = info[0]['transaction']
        r = await self.api.get_transaction(hash)
        logger.info(r)
        snapshot = await self.api.get_snapshot(r['snapshot'])
        logger.info(snapshot)

    @pytest.mark.asyncio
    async def test_list_mint_works(self):
        info = await self.api.list_mint_works(0)
        logger.info(info)

        info = await self.api.list_mint_works(1)
        logger.info(info)

    @pytest.mark.asyncio
    async def test_list_mint_distributions(self):
        info = await self.api.list_mint_distributions(0, 5, True)
        logger.info(info)

        info = await self.api.list_mint_distributions(1, 5, False)
        logger.info(info)

    @pytest.mark.asyncio
    async def test_get_round_by_number(self):
        r = await self.api.get_info()
        # logger.info(r)
        node = r['graph']['consensus'][0]['node']
        info = await self.api.get_round_by_number(node, 0)
        logger.info(info)

        info = await self.api.get_round_by_number(node, 1)
        logger.info(info)

    @pytest.mark.asyncio
    async def test_repeat_transfer(self):
        async def monitor():
            for i in range(7):
                n = self.nodes[i]
                try:
                    ret = n.wait(1.0)
                    if ret != 0:
                        logger.error(f'++++++++subprocess {i} exited abnormal: {ret}')
                except subprocess.TimeoutExpired:
                    pass
        # asyncio.create_task(monitor())

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
        with open('/tmp/mixin-7001/genesis.json', 'r') as f:
            genesis = f.read()
            genesis = json.loads(genesis)
            domain_node = genesis['domains'][0]
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
        
        await self.wait_for_transaction(deposit_hash)

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

            input_hash = await self.send_transaction(trx, [account])
            await self.wait_for_transaction(input_hash)

    @pytest.mark.asyncio
    async def test_transfer_with_cached_output_keys(self):
        async def monitor():
            for i in range(7):
                n = self.nodes[i]
                try:
                    ret = n.wait(1.0)
                    if ret != 0:
                        logger.error(f'++++++++subprocess {i} exited abnormal: {ret}')
                except subprocess.TimeoutExpired:
                    pass
        # asyncio.create_task(monitor())

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
        with open('/tmp/mixin-7001/genesis.json', 'r') as f:
            genesis = f.read()
            genesis = json.loads(genesis)
            domain_node = genesis['domains'][0]
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
        
        r = await self.wait_for_transaction(deposit_hash)
        logger.info(r)
        outputs = r['outputs']
        input_hash = deposit_hash
        for i in range(10):
            logger.info(f"+++++++++++++++transfer++++++++++++++++++++{i}")
            trx = {
                "asset": 'a99c2e0e2b1da4d648755ef19bd95139acbbe6564cfb06dec7cd34931ca72cdc',
                "inputs": [
                    {
                    "hash": input_hash,
                    "index": 0,
                    "keys": outputs[0]['keys'],
                    "mask": outputs[0]['mask'],
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

            input_hash = await self.send_transaction(trx, [account])
            r = await self.wait_for_transaction(input_hash)
            # logger.info(r)
            outputs = r['outputs']

    @pytest.mark.asyncio
    async def test_transfer_with_ghost_keys(self):
        async def monitor():
            for i in range(7):
                n = self.nodes[i]
                try:
                    ret = n.wait(1.0)
                    if ret != 0:
                        logger.error(f'++++++++subprocess {i} exited abnormal: {ret}')
                except subprocess.TimeoutExpired:
                    pass
        # asyncio.create_task(monitor())

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
        with open('/tmp/mixin-7001/genesis.json', 'r') as f:
            genesis = f.read()
            genesis = json.loads(genesis)
            domain_node = genesis['domains'][0]
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
        
        r = await self.wait_for_transaction(deposit_hash)
        logger.info(r)
        outputs = r['outputs']
        input_hash = deposit_hash
        for i in range(20):
            ghost_keys = self.api.new_ghost_keys('', [account['address']], 0)
            logger.info(f"+++++++++++++++transfer++++++++++++++++++++{i}")
            trx = {
                "asset": 'a99c2e0e2b1da4d648755ef19bd95139acbbe6564cfb06dec7cd34931ca72cdc',
                "inputs": [
                    {
                    "hash": input_hash,
                    "index": 0,
                    "keys": outputs[0]['keys'],
                    "mask": outputs[0]['mask'],
                    }
                ],
                "outputs": [
                    {
                    "amount": "100",
                    "accounts": [account['address']],
                    "script": "fffe01",
                    "type": 0,
                    'keys': ghost_keys['keys'],
                    'mask': ghost_keys['mask'],
                    },
                ]
            }
            params = {
                "seed": '', #account['spend_key'],
                "keys": [account['view_key'] + account['spend_key']],
                "raw": trx,
                "input_index": 0
            }
            # r = await self.api.get_info()
            input_hash = await self.send_transaction(trx, [account])
            r = await self.wait_for_transaction(input_hash)
            # logger.info(r)
            outputs = r['outputs']
            # logger.info('%s %s', ghost_keys, outputs)

    async def send_transaction(self, trx, accounts):
        for i in range(5):
            # self.api.set_node(f'http://127.0.0.1:8007')
            try:
                r = await self.api.send_transaction(trx, accounts)
                return r['hash']
                break
            except Exception as e:
                logger.info(e)
                await asyncio.sleep(0.4)
            i = random.randint(1, 7)
            # logger.info(i)
            self.api.set_node(f'http://127.0.0.1:800{i}')
        else:
            raise Exception('transfer failed!')

    async def wait_for_transaction(self, _hash):
        node_index = 1
        while True:
            try:
                r = await self.api.get_transaction(_hash)
                if not r:
                    await asyncio.sleep(0.1)
                    continue
                if 'snapshot' in r:
                    return r
                    # return await self.api.get_snapshot(r['snapshot'])
                    # logger.info(r)
                    break
            except Exception as e:
                logger.info(e)
                await asyncio.sleep(0.1)
            self.api.set_node(f'http://127.0.0.1:800{node_index}')
            node_index += 1
            if node_index > 7:
                node_index = 1

    @pytest.mark.asyncio
    async def test_multi_sign1(self):
        async def monitor():
            for i in range(7):
                n = self.nodes[i]
                try:
                    ret = n.wait(1.0)
                    if ret != 0:
                        logger.error(f'++++++++subprocess {i} exited abnormal: {ret}')
                except subprocess.TimeoutExpired:
                    pass
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
        with open('/tmp/mixin-7001/genesis.json', 'r') as f:
            genesis = f.read()
            genesis = json.loads(genesis)
            domain_node = genesis['domains'][0]
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

#        await asyncio.sleep(3.0)
        while True:
            r = await self.api.get_transaction(deposit_hash)
            if r and 'snapshot' in r:
                break
            await asyncio.sleep(0.2)
        # logger.info(r)

        input_hash = deposit_hash

        addresses = []
        accounts = []
        for i in range(255):
            addr = self.api.create_address()
            accounts.append(addr)
            addresses.append(addr['address'])

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
                "accounts": addresses,
                "script": "fffe40",
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

        input_hash = await self.send_transaction(trx, [account])
        await self.wait_for_transaction(input_hash)

        trx = {
            "asset": "a99c2e0e2b1da4d648755ef19bd95139acbbe6564cfb06dec7cd34931ca72cdc",
            "inputs": [
                {
                    "hash": input_hash,
                    "index": 0,
                }
            ],
            "Outputs":[
                {
                    "type": 0,
                    "amount": "100",
                    "script": 'fffe01',
                    "accounts": [
                        'XINFrqT5x74BVvtgLJEVhRhFc1GdJ3vmwiu7zJHVg7qjYvzx9wG7j1sENkXV7NfN9tQm1SsRNces7tcrxFas9nkr5H1B7HTm'                    ]
                }
            ],
            "extra": b"helloworld".hex(),
            # "-": ""
#            "Node":
        }
        r = self.api.sign_transaction(trx, accounts)
        raw = r['raw']
        signatures = r['signatures']
        r = await self.api.send_raw_transaction(raw)
        await self.wait_for_transaction(r['hash'])
        logger.info('done!')
        return

        params = {
            "input_index": "0",
            "raw": r['raw'],
            "trx": trx,
            "keys": keys
        }
        signatures = self.api.sign_raw_transaction(params)
        # logger.info(signatures)
        r = self.api.add_signatures_to_raw_transaction(r['raw'], signatures)
        # logger.info(r)
        r = await self.api.send_raw_transaction(r)
        await self.wait_for_transaction(r['hash'])
        logger.info('done!')



    @pytest.mark.asyncio
    async def test_multi_sign2(self):
        async def monitor():
            for i in range(7):
                n = self.nodes[i]
                try:
                    ret = n.wait(1.0)
                    if ret != 0:
                        logger.error(f'++++++++subprocess {i} exited abnormal: {ret}')
                except subprocess.TimeoutExpired:
                    pass
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
        with open('/tmp/mixin-7001/genesis.json', 'r') as f:
            genesis = f.read()
            genesis = json.loads(genesis)
            domain_node = genesis['domains'][0]
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

#        await asyncio.sleep(3.0)
        while True:
            r = await self.api.get_transaction(deposit_hash)
            if r and 'snapshot' in r:
                break
            await asyncio.sleep(0.2)
        # logger.info(r)

        input_hash = deposit_hash

        addresses = []
        accounts = []
        for i in range(255):
            addr = self.api.create_address()
            accounts.append(addr)
            addresses.append(addr['address'])

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
                "amount": "49",
                "accounts": addresses,
                "script": "fffe40",
                "type": 0
                },
                {
                "amount": "51",
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

        input_hash = await self.send_transaction(trx, [account])
        await self.wait_for_transaction(input_hash)

        trx = {
            "asset": "a99c2e0e2b1da4d648755ef19bd95139acbbe6564cfb06dec7cd34931ca72cdc",
            "inputs": [
                {
                    "hash": input_hash,
                    "index": 0,
                },
                {
                    "hash": input_hash,
                    "index": 1,
                }
            ],
            "Outputs":[
                {
                    "type": 0,
                    "amount": "100",
                    "script": 'fffe01',
                    "accounts": [
                        'XINFrqT5x74BVvtgLJEVhRhFc1GdJ3vmwiu7zJHVg7qjYvzx9wG7j1sENkXV7NfN9tQm1SsRNces7tcrxFas9nkr5H1B7HTm'
                        ]
                }
            ],
            "extra": b"helloworld".hex(),
            # "-": ""
#            "Node":
        }
        r = self.api.sign_transaction(trx, [])
        raw = r['raw']
        signatures = r['signatures']

        keys = []
        for i in range(64):
            keys.append(accounts[i]['view_key'] + accounts[i]['spend_key'])

        params = {
            "input_index": 0,
            "raw": r['raw'],
            "trx": trx,
            "keys": keys
        }
        input_0_signatures = self.api.sign_raw_transaction(params)
        # logger.info(input_0_signatures)

        params = {
            "input_index": 1,
            "raw": r['raw'],
            "trx": trx,
            "keys": [account['view_key'] + account['spend_key']]
        }
        input_1_signatures = self.api.sign_raw_transaction(params)
        # logger.info(input_1_signatures)

        signatures = [input_0_signatures[0], input_1_signatures[0]]
        r = self.api.add_signatures_to_raw_transaction(r['raw'], signatures)
        # logger.info(r)
        r = await self.api.send_raw_transaction(r)
        r = await self.wait_for_transaction(r['hash'])
        logger.info(r)
        logger.info('done!')
