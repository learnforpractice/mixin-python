# tests base on:
# https://prsdigg.com/articles/4375be62-6ef4-4de2-af9a-086816380fde
import os
import json
import time
import pytest
import asyncio
import subprocess
import httpx

from pymixin.mixin_api import MixinApi
from pymixin import log
from pymixin.testnet import MixinTestnet

logger = log.get_logger(__name__)

class TestMixinApi(object):

    @classmethod
    def setup_class(cls):
        cls.testnet = MixinTestnet()
        # cls.testnet.start()
        # cls.testnet.stop(cleanup=True)
        cls.testnet.start()

        cls.api = MixinApi('http://127.0.0.1:8001')

        loop = asyncio.get_event_loop()        
        async def wait():
            api = MixinApi('http://127.0.0.1:8007')
            await asyncio.sleep(2)
            while True:
                try:
                    await api.get_info()
                    return
                except Exception as e:
                    await asyncio.sleep(0.5)
                    logger.info(e)
        loop.run_until_complete(wait())

    @classmethod
    def teardown_class(cls):
        cls.testnet.stop(cleanup=True)

    def setup_method(self, method):
        logger.warning('test start: %s', method.__name__)

    def teardown_method(self, method):
        pass

    @pytest.mark.asyncio
    async def test_hello(self):
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
        async def monitor():
            for i in range(7):
                n = self.testnet.nodes[i]
                try:
                    ret = n.wait(1.0)
                    if ret != 0:
                        logger.error('++++++++subprocess {i} exited abnormal')
                except subprocess.TimeoutExpired:
                    pass
        asyncio.create_task(monitor())

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
        logger.info("++++++++++++++++++deposit+++++++++++++++")
        trx = {
            "asset": "a99c2e0e2b1da4d648755ef19bd95139acbbe6564cfb06dec7cd34931ca72cdc",
            "inputs": [{
                "deposit": {
                "chain": "8dd50817c082cdcdd6f167514928767a4b52426997bd6d4930eca101c5ff8a27",
                "asset": "0xa974c709cfb4566686553a20790685a47aceaa33",
                "transaction": "0x4cb581281f7115706c5e6f669371574bfdea317325e15eef32cd356df0d4788b",
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

        address = self.testnet.node_addresses[0]['signer']
        params = {
            "seed": '', #account['spend_key'],
            "keys": [address['view_key'] + address['spend_key']],
            "raw": trx,
            "input_index": 0
        }
        r = self.api.sign_transaction(trx, [address])
        # logger.info(r)
        r = await self.api.send_raw_transaction(r['raw'])
        # logger.info(r)
        deposit_hash = r['hash']

        while True:
            r = await self.api.get_transaction(deposit_hash)
            if r:
                break
            logger.info('++++get_transaction(%s), retrying...', deposit_hash)
            await asyncio.sleep(0.5)
        # logger.info(r)

        logger.info("++++++++++++++++++transfer+++++++++++++++")
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

        for i in range(10):
            try:
                r = self.api.sign_transaction(trx, [account])
                # logger.info(r)
                transfer_ret = await self.api.send_raw_transaction(r['raw'])
                break
            except Exception as e:
                logger.info(e)
                await asyncio.sleep(1.0)

        else:
            raise Exception('transfer test failed!')
        # logger.info(transfer_ret)

        logger.info("++++++++++++++++++withdraw+++++++++++++++")
        trx = {
            "asset": "a99c2e0e2b1da4d648755ef19bd95139acbbe6564cfb06dec7cd34931ca72cdc",
            "extra": b"hello,world".hex(),
            "inputs": [
                {
                "hash": transfer_ret['hash'],
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

        await asyncio.sleep(2.0)
        for i in range(10):
            try:
                r = self.api.sign_transaction(trx, [account])
                # logger.info(r)
                transfer_ret = await self.api.send_raw_transaction(r['raw'])
                break
            except Exception as e:
                logger.info(e)
                await asyncio.sleep(1.0)




