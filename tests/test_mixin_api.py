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
import threading
from io import BytesIO
import httpx

from mixin.mixin_api import MixinApi
from mixin.mixin_bot_api import MixinBotApi
from mixin import mixin_config
from mixin import log

logger = log.get_logger(__name__)

class TestMixinApi(object):

    @classmethod
    def setup_class(cls):
        cls.bot = MixinBotApi(mixin_config)
        cls.api = MixinApi('http://mixin-node0.exinpool.com:8239')

    @classmethod
    def teardown_class(cls):
        pass

    def setup_method(self, method):
        logger.warning('test start: %s', method.__name__)

    def teardown_method(self, method):
        pass

    def test_create_address(self):
        r = self.api.create_address()
        logger.warning(r)

        args = {
            "view_key": "",
            "spend_key": "",
            "public":False
        }
        address = self.api.create_address(**args)
        addr = address['address']
        decoded_address = self.api.decode_address(addr)
        assert decoded_address['public_spend_key'] == self.api.get_public_key(address['spend_key'])
        assert decoded_address['public_view_key'] == self.api.get_public_key(address['view_key'])

        # Specify view_key
        args = {
            "view_key": "8d4a7902b87af98b86aef7df48599a129389b97fbce9be3a095497cd1fc21308",
            "spend_key": "",
            "public":False
        }
        r = self.api.create_address(**args)
        assert r['view_key'] == args['view_key']

        args = {
            "view_key": "",
            "spend_key": "8d4a7902b87af98b86aef7df48599a129389b97fbce9be3a095497cd1fc21308",
            "public":False
        }
        r = self.api.create_address(**args)
        assert r['spend_key'] == args['spend_key']

        args = {
            "view_key": "8d4a7902b87af98b86aef7df48599a129389b97fbce9be3a095497cd1fc21308",
            "spend_key": "e61eda099a3b99d685c23d0ac7f6704bb9c279db90b4d71cd4014d07f4256d07",
            "public":False
        }
        r = self.api.create_address(**args)
        assert r['view_key'] == args['view_key']
        assert r['spend_key'] == args['spend_key']

        args = {
            "view_key": "8d4a7902b87af98b86aef7df48599a129389b97fbce9be3a095497cd1fc21308",
            "spend_key": "e61eda099a3b99d685c23d0ac7f6704bb9c279db90b4d71cd4014d07f4256d07",
            "public":True
        }
        r = self.api.create_address(**args)
        assert not r['view_key'] == args['view_key']
        assert r['spend_key'] == args['spend_key']

    def test_decode_address(self):
        addr = self.api.create_address()
        logger.info(addr)
        r = self.api.decode_address(addr['address'])
        logger.warning(r)

    def test_decode_signature(self):
        signature = '81a085ca768adc4901b5484ecc3cdbb4eee68307f78cd5ea041d7d4425496bd100000000000000000000000000000000000000000000000000000000000000000000000000fffc7f'
        signature = 'bd1892cf5865e0c2c6597c1497113be12fcba611e32058146a8bfcd81aa0a099e3de93fbb28f8ded97f1529c5b3a7f20bdf305f0195be66cf2453b11b8cfb3080000000000fffc7f'
        r = self.api.decode_signature(signature)
        logger.info(r)

    @pytest.mark.asyncio
    async def test_get_info(self):
        r = await self.api.get_info()
        logger.info(r)

    def test_decode_transaction(self):
        raw = '77770002b9f49cf777dc4d03bc54cd1367eebca319f8603ea1ce18910d09e2c540c630d80001f8d33203a8f7f1e1e105ae3556b2d1f3f790c4420bc2487338413d2639177f24000100000000000000020000000405f5e1000003dd6ef36bc256cc18c917bf621f184e34738f76c813d37955a28ac47366a6b0c2a31a6c2feb99d12ccfdbe085f26b66adc13d2ac5c1fdf80e652205f2632f9d9bffff86b5066faeadf35d6d649d71e4664b3fe2df56f640cedc1a40bd837fdcf648d6082327918871b0946c376d783ebbcd439d52b703f2c7f62233fdd47487520003fffe0200000000000703ab00738ad50000014c31ca69ed35ad79136a8706c8caf810bcd8efedb2f56bb3d2934f0232dc62f87e2744078936c1a1e7f487ec0ca61158071aafd64942f52a6d9d3796cced68250003fffe010000004882a154c41000000000000000000000000000000000a14dd92f66333262623661622d316134642d343462622d383932662d6630313239323339646638392d2d637265617465616363000100010000bd1892cf5865e0c2c6597c1497113be12fcba611e32058146a8bfcd81aa0a099e3de93fbb28f8ded97f1529c5b3a7f20bdf305f0195be66cf2453b11b8cfb308'
        r = self.api.decode_transaction(raw)
        logger.info(r)

    def test_encode_transaction(self):
        r = {'asset': 'b9f49cf777dc4d03bc54cd1367eebca319f8603ea1ce18910d09e2c540c630d8',
        'extra': '82a154c41000000000000000000000000000000000a14dd92f66333262623661622d316134642d343462622d383932662d6630313239323339646638392d2d637265617465616363',
        'hash': 'cbc9b9dcfa6311974a66fae92dddb4166d9a3cb36b4968d08cc311d9863b3721',
        'inputs': [{'hash': 'f8d33203a8f7f1e1e105ae3556b2d1f3f790c4420bc2487338413d2639177f24',
        'index': 1}],
        'outputs': [{'amount': '1.00000000',
        'keys': ['dd6ef36bc256cc18c917bf621f184e34738f76c813d37955a28ac47366a6b0c2',
            'a31a6c2feb99d12ccfdbe085f26b66adc13d2ac5c1fdf80e652205f2632f9d9b',
            'ffff86b5066faeadf35d6d649d71e4664b3fe2df56f640cedc1a40bd837fdcf6'],
        'mask': '48d6082327918871b0946c376d783ebbcd439d52b703f2c7f62233fdd4748752',
        'script': 'fffe02',
        'type': 0},
        {'amount': '10324433.56960000',
        'keys': ['4c31ca69ed35ad79136a8706c8caf810bcd8efedb2f56bb3d2934f0232dc62f8'],
        'mask': '7e2744078936c1a1e7f487ec0ca61158071aafd64942f52a6d9d3796cced6825',
        'script': 'fffe01',
        'type': 0}],
        'signatures': [{'0': 'bd1892cf5865e0c2c6597c1497113be12fcba611e32058146a8bfcd81aa0a099e3de93fbb28f8ded97f1529c5b3a7f20bdf305f0195be66cf2453b11b8cfb308'}],
        'version': 2
        }

        r['signatures'].append({"1": r['signatures'][0]["0"]})
        r = self.api.encode_transaction(r, r['signatures'])
        logger.info(r)

        r = self.api.decode_transaction(r)
        logger.info(r)

    def test_sign_transaction(self):
        account = {
            'address': 'XINFrqT5x74BVvtgLJEVhRhFc1GdJ3vmwiu7zJHVg7qjYvzx9wG7j1sENkXV7NfN9tQm1SsRNces7tcrxFas9nkr5H1B7HTm',
            'view_key': 'bd1a337f2319d502eb062a433cb79cf8e2daadd6bcd0bb2a21d4b073549cb30c',
            'spend_key': 'bd449970bdb5cf9afaf1f9c574a94f06ff7a0d3af0d9387867e1ba7e9193eb03'
        }

# {'address': 'XINJAJUFCWSQJa3tMNte3biMwXPEs4ptbVvBho17R48zUYXyDgn4eLgc58P2fdhQ6CnYzpGtNtjDb7XaNmx6JJrsawUq1VjC',
#  'view_key': '7f6209043a7238eaba761e8c0aa354c7dff5cd166d4fb6ede229d484a2c6e40a',
#  'spend_key': '1decce01df980cf27bcedbfed2c7bb8a4a99ed73e63502640718f7ce93192202'}

        # type signerInput struct {
        # 	Inputs []struct {
        # 		Hash    crypto.Hash `json:"hash"`
        # 		Index   int         `json:"index"`
        # 		Deposit *struct {
        # 			Chain           crypto.Hash    `json:"chain"`
        # 			AssetKey        string         `json:"asset"`
        # 			TransactionHash string         `json:"transaction"`
        # 			OutputIndex     uint64         `json:"index"`
        # 			Amount          common.Integer `json:"amount"`
        # 		} `json:"deposit,omitempty"`
        # 		Keys []crypto.Key `json:"keys"`
        # 		Mask crypto.Key   `json:"mask"`
        # 	} `json:"inputs"`
        # 	Outputs []struct {
        # 		Type     uint8             `json:"type"`
        # 		Mask     crypto.Key        `json:"mask"`
        # 		Keys     []crypto.Key      `json:"keys"`
        # 		Amount   common.Integer    `json:"amount"`
        # 		Script   common.Script     `json:"script"`
        # 		Accounts []*common.Address `json:"accounts"`
        # 	}
        # 	Asset crypto.Hash `json:"asset"`
        # 	Extra string      `json:"extra"`
        # 	Node  string      `json:"-"`
        # }
        trx = {
            "inputs": [
                {
                    "hash": 'e26f9dd1afc7dd5a216019f27f369a7123ade2c20b7ea07602b218e281ba93e4',
                    "index": 0,
                    # "keys": [],
                    # "mask": '0'*64
                }
            ],
            "Outputs":[
                {
                    "type": 0,
                    # "mask" :"b3f9f76c5be32ba2c90de2a6442cb3b0356d79c2241ddc87109822e9ea31ae49",
                    # "keys": ["0da9d5806be84cedf0f029ce9cb9b5dc4d23dc019f802d9e5b0d6377c3bfb3e9"],
                    "amount": "0.1",
                    "script": 'fffe01',
                    "accounts": [
                        'XINFrqT5x74BVvtgLJEVhRhFc1GdJ3vmwiu7zJHVg7qjYvzx9wG7j1sENkXV7NfN9tQm1SsRNces7tcrxFas9nkr5H1B7HTm']
                },
                {
                    "type": 0,
                    # "mask" :"b3f9f76c5be32ba2c90de2a6442cb3b0356d79c2241ddc87109822e9ea31ae49",
                    # "keys": ["0da9d5806be84cedf0f029ce9cb9b5dc4d23dc019f802d9e5b0d6377c3bfb3e9"],
                    "amount": "0.9",
                    "script": 'fffe01',
                    "accounts": [
                        'XINJAJUFCWSQJa3tMNte3biMwXPEs4ptbVvBho17R48zUYXyDgn4eLgc58P2fdhQ6CnYzpGtNtjDb7XaNmx6JJrsawUq1VjC']
                },
            ],
            "asset": "b9f49cf777dc4d03bc54cd1367eebca319f8603ea1ce18910d09e2c540c630d8",
            "extra": b"helloworld".hex(),
            # "-": ""
#            "Node":
        }
        params = {
            "seed": '', #account['spend_key'],
            "key": json.dumps([account['view_key'] + account['spend_key']]),
            "raw": json.dumps(trx),
            "inputIndex": "0"
        }
        r = self.api.sign_transaction(params)
        logger.info(r)

    def test_sign_transaction2(self):
        account = {
            'address': 'XINFrqT5x74BVvtgLJEVhRhFc1GdJ3vmwiu7zJHVg7qjYvzx9wG7j1sENkXV7NfN9tQm1SsRNces7tcrxFas9nkr5H1B7HTm',
            'view_key': 'bd1a337f2319d502eb062a433cb79cf8e2daadd6bcd0bb2a21d4b073549cb30c',
            'spend_key': 'bd449970bdb5cf9afaf1f9c574a94f06ff7a0d3af0d9387867e1ba7e9193eb03'
        }

# {'address': 'XINJAJUFCWSQJa3tMNte3biMwXPEs4ptbVvBho17R48zUYXyDgn4eLgc58P2fdhQ6CnYzpGtNtjDb7XaNmx6JJrsawUq1VjC',
#  'view_key': '7f6209043a7238eaba761e8c0aa354c7dff5cd166d4fb6ede229d484a2c6e40a',
#  'spend_key': '1decce01df980cf27bcedbfed2c7bb8a4a99ed73e63502640718f7ce93192202'}

        # type signerInput struct {
        # 	Inputs []struct {
        # 		Hash    crypto.Hash `json:"hash"`
        # 		Index   int         `json:"index"`
        # 		Deposit *struct {
        # 			Chain           crypto.Hash    `json:"chain"`
        # 			AssetKey        string         `json:"asset"`
        # 			TransactionHash string         `json:"transaction"`
        # 			OutputIndex     uint64         `json:"index"`
        # 			Amount          common.Integer `json:"amount"`
        # 		} `json:"deposit,omitempty"`
        # 		Keys []crypto.Key `json:"keys"`
        # 		Mask crypto.Key   `json:"mask"`
        # 	} `json:"inputs"`
        # 	Outputs []struct {
        # 		Type     uint8             `json:"type"`
        # 		Mask     crypto.Key        `json:"mask"`
        # 		Keys     []crypto.Key      `json:"keys"`
        # 		Amount   common.Integer    `json:"amount"`
        # 		Script   common.Script     `json:"script"`
        # 		Accounts []*common.Address `json:"accounts"`
        # 	}
        # 	Asset crypto.Hash `json:"asset"`
        # 	Extra string      `json:"extra"`
        # 	Node  string      `json:"-"`
        # }
        trx = {
            "inputs": [
                {
                    "hash": '0a121a7d64e2d01c6efb4cf23734655b2cb1cf65b54eaa330ad6da643875e938',
                    "index": 0,
                    # "keys": [],
                    # "mask": '0'*64
                }
            ],
            "Outputs":[
                {
                    "type": 0,
                    # "mask" :"b3f9f76c5be32ba2c90de2a6442cb3b0356d79c2241ddc87109822e9ea31ae49",
                    # "keys": ["0da9d5806be84cedf0f029ce9cb9b5dc4d23dc019f802d9e5b0d6377c3bfb3e9"],
                    "amount": "0.1",
                    "script": 'fffe02',
                    "accounts": [
                        'XINFrqT5x74BVvtgLJEVhRhFc1GdJ3vmwiu7zJHVg7qjYvzx9wG7j1sENkXV7NfN9tQm1SsRNces7tcrxFas9nkr5H1B7HTm',
                        'XINJAJUFCWSQJa3tMNte3biMwXPEs4ptbVvBho17R48zUYXyDgn4eLgc58P2fdhQ6CnYzpGtNtjDb7XaNmx6JJrsawUq1VjC'
                        ]
                },
            ],
            "asset": "b9f49cf777dc4d03bc54cd1367eebca319f8603ea1ce18910d09e2c540c630d8",
            "extra": b"helloworld".hex(),
            # "-": ""
#            "Node":
        }
        params = {
            "seed": '', #account['spend_key'],
            "key": json.dumps([account['view_key'] + account['spend_key']]),
            "raw": json.dumps(trx),
            "inputIndex": "0"
        }
        r = self.api.sign_transaction(params)
        logger.info(r)

    def test_multi_sign_transaction(self):
        account = {
            'address': 'XINFrqT5x74BVvtgLJEVhRhFc1GdJ3vmwiu7zJHVg7qjYvzx9wG7j1sENkXV7NfN9tQm1SsRNces7tcrxFas9nkr5H1B7HTm',
            'view_key': 'bd1a337f2319d502eb062a433cb79cf8e2daadd6bcd0bb2a21d4b073549cb30c',
            'spend_key': 'bd449970bdb5cf9afaf1f9c574a94f06ff7a0d3af0d9387867e1ba7e9193eb03'
        }

        account2 = {
            'address': 'XINJAJUFCWSQJa3tMNte3biMwXPEs4ptbVvBho17R48zUYXyDgn4eLgc58P2fdhQ6CnYzpGtNtjDb7XaNmx6JJrsawUq1VjC',
            'view_key': '7f6209043a7238eaba761e8c0aa354c7dff5cd166d4fb6ede229d484a2c6e40a',
            'spend_key': '1decce01df980cf27bcedbfed2c7bb8a4a99ed73e63502640718f7ce93192202'
        }

        # type signerInput struct {
        # 	Inputs []struct {
        # 		Hash    crypto.Hash `json:"hash"`
        # 		Index   int         `json:"index"`
        # 		Deposit *struct {
        # 			Chain           crypto.Hash    `json:"chain"`
        # 			AssetKey        string         `json:"asset"`
        # 			TransactionHash string         `json:"transaction"`
        # 			OutputIndex     uint64         `json:"index"`
        # 			Amount          common.Integer `json:"amount"`
        # 		} `json:"deposit,omitempty"`
        # 		Keys []crypto.Key `json:"keys"`
        # 		Mask crypto.Key   `json:"mask"`
        # 	} `json:"inputs"`
        # 	Outputs []struct {
        # 		Type     uint8             `json:"type"`
        # 		Mask     crypto.Key        `json:"mask"`
        # 		Keys     []crypto.Key      `json:"keys"`
        # 		Amount   common.Integer    `json:"amount"`
        # 		Script   common.Script     `json:"script"`
        # 		Accounts []*common.Address `json:"accounts"`
        # 	}
        # 	Asset crypto.Hash `json:"asset"`
        # 	Extra string      `json:"extra"`
        # 	Node  string      `json:"-"`
        # }
        trx = {
            "inputs": [
                {
                    "hash": '28416305558388eed2cc12d0a6fe32201371f631d86751736f591120d3d2b07e',
                    "index": 0,
                    # "keys": [],
                    # "mask": '0'*64
                }
            ],
            "Outputs":[
                {
                    "type": 0,
                    # "mask" :"b3f9f76c5be32ba2c90de2a6442cb3b0356d79c2241ddc87109822e9ea31ae49",
                    # "keys": ["0da9d5806be84cedf0f029ce9cb9b5dc4d23dc019f802d9e5b0d6377c3bfb3e9"],
                    "amount": "0.1",
                    "script": 'fffe01',
                    "accounts": [
                        'XINFrqT5x74BVvtgLJEVhRhFc1GdJ3vmwiu7zJHVg7qjYvzx9wG7j1sENkXV7NfN9tQm1SsRNces7tcrxFas9nkr5H1B7HTm'                    ]
                }
            ],
            "asset": "b9f49cf777dc4d03bc54cd1367eebca319f8603ea1ce18910d09e2c540c630d8",
            "extra": b"helloworld".hex(),
            # "-": ""
#            "Node":
        }
        params = {
            "seed": '', #account['spend_key'],
            "key": json.dumps([account['view_key'] + account['spend_key']]),
            "raw": json.dumps(trx),
            "inputIndex": "0"
        }
        r = self.api.sign_transaction(params)
        logger.info(r)
        signatures = {}
 
        # r = self.api.decode_transaction(r['raw'])
        # logger.info(r)
 
        params = {
            "input_index": "0",
            "raw": r['raw'],
            "trx": json.dumps(trx),
            "keys": json.dumps([account['view_key'] + account['spend_key']]),
        }
        signature = self.api.sign_raw_transaction(params)
        logger.info(signature)
        signatures = signature

        params = {
            "input_index": "0",
            "raw": r['raw'],
            "trx": json.dumps(trx),
            "keys": json.dumps([account2['view_key'] + account2['spend_key']]),
        }
        signature = self.api.sign_raw_transaction(params)
        logger.info(signature)
        signatures[0].update(signature[0])

        r = self.api.add_signatures_to_raw_transaction(r['raw'], signatures)
        logger.info(r)

        r = self.api.decode_transaction(r)
        logger.info(r)
    def test_add_signatures_to_raw_transaction(self):

        self.api.add_signatures_to_raw_transaction()

# seed, err := hex.DecodeString(c.String("seed"))
# viewKey, err := crypto.KeyFromString(c.String("view"))
# spendKey, err := crypto.KeyFromString(c.String("spend"))
# asset, err := crypto.HashFromString(c.String("asset"))
# extra, err := hex.DecodeString(c.String("extra"))
# for _, in := range strings.Split(c.String("inputs"), ",") {
# for _, out := range strings.Split(c.String("outputs"), ",") {

    def test_build_raw_transaction(self):
        account = {
            'address': 'XINFrqT5x74BVvtgLJEVhRhFc1GdJ3vmwiu7zJHVg7qjYvzx9wG7j1sENkXV7NfN9tQm1SsRNces7tcrxFas9nkr5H1B7HTm',
            'view_key': 'bd1a337f2319d502eb062a433cb79cf8e2daadd6bcd0bb2a21d4b073549cb30c',
            'spend_key': 'bd449970bdb5cf9afaf1f9c574a94f06ff7a0d3af0d9387867e1ba7e9193eb03'
        }
        params = {
            'seed': 'a'*64*2,
            'view': 'bd1a337f2319d502eb062a433cb79cf8e2daadd6bcd0bb2a21d4b073549cb30c',
            'spend': 'bd449970bdb5cf9afaf1f9c574a94f06ff7a0d3af0d9387867e1ba7e9193eb03',
            'asset': 'b9f49cf777dc4d03bc54cd1367eebca319f8603ea1ce18910d09e2c540c630d8',
            'extra': b'hello,world'.hex(),
            'inputs': '7a5e528c819aa3109c6354cbddba90e7a3b1cafbdc3641f165c49a144537f5ca:0',
            'outputs':'XINFrqT5x74BVvtgLJEVhRhFc1GdJ3vmwiu7zJHVg7qjYvzx9wG7j1sENkXV7NfN9tQm1SsRNces7tcrxFas9nkr5H1B7HTm:10.0',
            'node': 'http://mixin-node0.exinpool.com:8239'
        }
        r = self.api.build_raw_transaction(params)
        logger.info(r)
        r = self.api.decode_transaction(r)
        logger.info(r)

    def test_build_transaction_with_ghost_keys(self):
        print("++++test_build_transaction_with_ghost_keys")
        cnb_asset_id = 'b9f49cf777dc4d03bc54cd1367eebca319f8603ea1ce18910d09e2c540c630d8'
        ghost_keys = '[{"type": "ghost_key", "mask": "8b16a69e02a8fd5cfed51c8525e33cb1da6fa8d3e503807a1cc9f2a9906a0826", "keys": ["3478c1f159913ed5c7fb3d2ab7bb5cde374b76bfe749d501c060a689ea1880d3"]}]'
        trx_hash = 'a97cb6d12e211553d62e4a19f5e40589d1b8bfeb5540ebd63936736c22f3307c'
        output_amount = '["1"]'
        output_index = 1
        memo = b'hello,world'.hex()
        raw = self.api.build_transaction_with_ghost_keys(cnb_asset_id, ghost_keys, trx_hash, output_amount, memo, output_index)

        memo = b'hello,world'
        raw = self.api.build_transaction_with_ghost_keys(cnb_asset_id, ghost_keys, trx_hash, output_amount, memo, output_index)

        memo = 'a'*200
        raw = self.api.build_transaction_with_ghost_keys(cnb_asset_id, ghost_keys, trx_hash, output_amount, memo, output_index)
        logger.info('++++')

        with pytest.raises(AssertionError) as execinfo:
            memo = 'a'*257
            raw = self.api.build_transaction_with_ghost_keys(cnb_asset_id, ghost_keys, trx_hash, output_amount, memo, output_index)
        logger.info(execinfo.value)

    def test_signature(self):
        # addr = self.api.create_address()
        # spend_key = addr['spend_key']
        # logger.info(spend_key)

        spend_key = "a9d9e97b983bc1fbff5f4c89b8789918d45c9318b1edf460b4fa1a5c4177670b"

        msg = 'hello,world'
        signature = self.api.sign_message(spend_key, msg)
        logger.info(signature)
        pub_key = self.api.get_public_key(spend_key)
        logger.info(pub_key)
        assert self.api.verify_signature(msg, pub_key, signature)

    def test_batch_verify(self):
        spend_key = "a9d9e97b983bc1fbff5f4c89b8789918d45c9318b1edf460b4fa1a5c4177670b"
        spend_key2 = "7ae37024eb14d00162f66e290649dbafb2abe4ee67a6190b63854f10a706dc0e"

        msg = 'hello,world'
        signature = self.api.sign_message(spend_key, msg)
        pub_key = self.api.get_public_key(spend_key)
        pub_key = bytes.fromhex(pub_key)
        signature = bytes.fromhex(signature)

        # ret = self.api.batch_verify(msg, [pub_key], [signature])
        # logger.info(ret)

        signature2 = self.api.sign_message(spend_key2, msg)
        pub_key2 = self.api.get_public_key(spend_key2)
        pub_key2 = bytes.fromhex(pub_key2)
        signature2 = bytes.fromhex(signature2)

        ret = self.api.batch_verify(msg, [pub_key, pub_key2], [signature, signature2])
        logger.info(ret)

    def test_asset_id(self):
        #XIN asset id
        asset = {
            'chain_id':'8dd50817c082cdcdd6f167514928767a4b52426997bd6d4930eca101c5ff8a27',
            'asset_key':'0xa974c709cfb4566686553a20790685a47aceaa33'
        }
        ret = self.api.get_asset_id(asset)
        logger.info(ret)
        assert ret == 'a99c2e0e2b1da4d648755ef19bd95139acbbe6564cfb06dec7cd34931ca72cdc'

        #ETH asset id
        asset = {
            'chain_id':'8dd50817c082cdcdd6f167514928767a4b52426997bd6d4930eca101c5ff8a27',
            'asset_key':'0x0000000000000000000000000000000000000000'
        }
        ret = self.api.get_asset_id(asset)
        logger.info(ret)
        assert ret == '8dd50817c082cdcdd6f167514928767a4b52426997bd6d4930eca101c5ff8a27'

        ret = self.api.get_fee_asset_id(asset)
        logger.info(ret)
        assert ret == '8dd50817c082cdcdd6f167514928767a4b52426997bd6d4930eca101c5ff8a27'

        # EOS asset id
        asset = {
            'chain_id':'6ac4cbffda9952e7f0d924e4cfb6beb29d21854ac00bfbf749f086302d0f7e5d',
            'asset_key':"eosio.token:EOS"
        }
        ret = self.api.get_asset_id(asset)
        logger.info('EOS asset id: %s', ret)
        assert ret == '6ac4cbffda9952e7f0d924e4cfb6beb29d21854ac00bfbf749f086302d0f7e5d'

        #EOS USDT asset id
        asset = {
            'chain_id':'6ac4cbffda9952e7f0d924e4cfb6beb29d21854ac00bfbf749f086302d0f7e5d',
            'asset_key':"tethertether:USDT"
        }
        ret = self.api.get_asset_id(asset)
        logger.info('USDT asset id:%s', ret)

    def test_decode_host_key(self):
        # view, err := crypto.KeyFromString(ghostKey["view"])
        # key, err := crypto.KeyFromString(ghostKey["key"])
        # mask, err := crypto.KeyFromString(ghostKey["mask"])
        # n, err := strconv.ParseUint(ghostKey["index"], 10, 64)
        params = {
            'view':'bd1a337f2319d502eb062a433cb79cf8e2daadd6bcd0bb2a21d4b073549cb30c',
            'key':'961cd15051274f6d896750c69e44c5ff9bca27e81691667ee344e953b3255601',
            'mask':'a56db149223a6872ee35d8c7bb0dfef140669913119ffe56a7f06a18a309a61b',
            'index':'0'
        }
        ret = self.api.decode_ghost_key(params)
        logger.info(ret)
        assert ret == 'XINFrqT5x74BVvtgLJEVhRhFc1GdJ3vmwiu7zJHVg7qjYvzx9wG7j1sENkXV7NfN9tQm1SsRNces7tcrxFas9nkr5H1B7HTm'

    @pytest.mark.asyncio
    async def test_async(self):
        import httpx
        logger.warning("+++++++=test_async")
        logger.info("+++++++=test_async")
        print('++++++=test_async')
        async with httpx.AsyncClient() as client:
            response = await client.get("http://www.google.com")

    @pytest.mark.asyncio
    async def test_gen_pin(self):
        r = await self.bot.verifyPin()
        assert not 'error' in r
        logger.info(r)
