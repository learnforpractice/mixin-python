import os
import json
import time
import ctypes
import logging
import uuid
import base64
import gzip
import random
import threading
from io import BytesIO
import httpx

from .mixin_bot_api import MixinBotApi
from .import mixin_config
from .import log
from . import _mixin

logger = log.get_logger(__name__)

class MixinApi(object):

    def __init__(self, url):
        self.node_url = url
        self.api = MixinBotApi(mixin_config)
        self.client = httpx.AsyncClient()
        self.init()

    def init(self):
        _mixin.init()

    def set_node(self, url):
        self.node_url = url

    def create_address(self, params={}):
        ret = _mixin.create_address(json.dumps(params))
        ret = json.loads(ret)
        if 'error' in ret:
            raise Exception(ret['error'])
        return ret['data']

    def get_public_key(self, seed):
        ret = _mixin.get_public_key(seed)
        ret = json.loads(ret)
        if 'error' in ret:
            raise Exception(ret['error'])
        return ret['data']

    def decode_address(self, addr):
        ret = _mixin.decode_address(addr)
        ret = json.loads(ret)
        if 'error' in ret:
            raise Exception(ret['error'])
        return ret['data']

    def decode_signature(self, sig):
        ret = _mixin.decode_signature(sig)
        ret = json.loads(ret)
        if 'error' in ret:
            raise Exception(ret['error'])
        return ret['data']

    def decode_ghost_key(self, key):
        ret = _mixin.decrypt_ghost(key)
        ret = json.loads(ret)
        if 'error' in ret:
            raise Exception(ret['error'])
        return ret['data']

    def decode_transaction(self, raw):
        ret = _mixin.decode_transaction(raw)
        ret = json.loads(ret)
        if 'error' in ret:
            raise Exception(ret['error'])
        return json.loads(ret['data'])

    def encode_transaction(self, trx, signs):
        if isinstance(trx, dict):
            trx = json.dumps(trx)
        signs = json.dumps(signs)
        ret = _mixin.encode_transaction(trx, signs)
        ret = json.loads(ret)
        if 'error' in ret:
            raise Exception(ret['error'])
        return ret['data']

    def sign_raw_transaction(self, params):
        '''
        raw
        trx
        keys
        node
        '''
        params["node"] = self.node_url
        params = json.dumps(params)
        ret = _mixin.sign_raw_transaction(params)
        ret = json.loads(ret)
        if 'error' in ret:
            raise Exception(ret['error'])
        return json.loads(ret['data'])

    def add_signatures_to_raw_transaction(self, raw, signs):
        signs = json.dumps(signs)
        ret = _mixin.add_signatures_to_raw_transaction(raw, signs)
        ret = json.loads(ret)
        if 'error' in ret:
            raise Exception(ret['error'])
        return ret['data']

# seed, err := hex.DecodeString(c.String("seed"))
# viewKey, err := crypto.KeyFromString(c.String("view"))
# spendKey, err := crypto.KeyFromString(c.String("spend"))
# asset, err := crypto.HashFromString(c.String("asset"))
# extra, err := hex.DecodeString(c.String("extra"))
# for _, in := range strings.Split(c.String("inputs"), ",") {
# for _, out := range strings.Split(c.String("outputs"), ",") {

    def build_raw_transaction(self, params):
        '''
        Example:
        api = MixinApi('http://mixin-node0.exinpool.com:8239')
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
        r = api.build_raw_transaction(params)
        '''
        if isinstance(params, dict):
            params = json.dumps(params)
        ret = _mixin.build_raw_transaction(params)
        ret = json.loads(ret)
        if 'error' in ret:
            raise Exception(ret['error'])
        return ret['data']

    def build_transaction_with_ghost_keys(self, asset_id, ghost_keys, trx_hash, output_amount, memo, output_index):
        if not isinstance(memo, bytes):
            memo = str(memo)
            memo = memo.encode('utf8')
        assert len(memo) <= 256, 'memo must <= 256 bytes'
        memo = memo.hex()
        ret = _mixin.build_transaction_with_ghost_keys(asset_id, ghost_keys, trx_hash, output_amount, memo, output_index)
        ret = json.loads(ret)
        if 'error' in ret:
            raise Exception(ret['error'])
        return ret['data']

    def sign_transaction(self, params):
        '''
        type signerInput struct {
            Inputs []struct {
                Hash    crypto.Hash `json:"hash"`
                Index   int         `json:"index"`
                Deposit *struct {
                    Chain           crypto.Hash    `json:"chain"`
                    AssetKey        string         `json:"asset"`
                    TransactionHash string         `json:"transaction"`
                    OutputIndex     uint64         `json:"index"`
                    Amount          common.Integer `json:"amount"`
                } `json:"deposit,omitempty"`
                Keys []crypto.Key `json:"keys"`
                Mask crypto.Key   `json:"mask"`
            } `json:"inputs"`
            Outputs []struct {
                Type     uint8             `json:"type"`
                Mask     crypto.Key        `json:"mask"`
                Keys     []crypto.Key      `json:"keys"`
                Amount   common.Integer    `json:"amount"`
                Script   common.Script     `json:"script"`
                Accounts []*common.Address `json:"accounts"`
            }
            Asset crypto.Hash `json:"asset"`
            Extra string      `json:"extra"`
            Node  string      `json:"-"`
        }
        {
            "raw":
            "seed":
            "key":
        }
        '''
        params["node"] = self.node_url
        if isinstance(params, dict):
            params = json.dumps(params)
        ret = _mixin.sign_transaction(params)
        ret = json.loads(ret)
        if 'error' in ret:
            raise Exception(ret['error'])
        ret = ret['data']
        ret['signature'] = json.loads(ret['signature'])
        return ret

    async def get_info(self):
        data = {'method': 'getinfo', 'params': []}
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        r = await self.client.post(self.node_url, json=data, headers=headers)
        return r.json()

    async def send_transaction(self, raw):
        data = {'method': 'sendrawtransaction', 'params': [raw]}
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        r = await self.client.post(self.node_url, json=data, headers=headers)
        return r.json()

    async def get_transaction(self, trx_hash):
        data = {'method': 'gettransaction', 'params': [trx_hash]}
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        r = await self.client.post(self.node_url, json=data, headers=headers)
        return json.loads(r.text)

    def pledge_node(self, params):
        if isinstance(params, dict):
            params = json.dumps(params)
        ret = _mixin.pledge_node(params)
        ret = json.loads(ret)
        if 'error' in ret:
            raise Exception(ret['error'])
        return ret['data']

    def cancel_node(self, params):
        if isinstance(params, dict):
            params = json.dumps(params)
        ret = _mixin.cancel_node(params)
        ret = json.loads(ret)
        if 'error' in ret:
            raise Exception(ret['error'])
        return ret['data']

    def decode_pledge_node(self, params):
        if isinstance(params, dict):
            params = json.dumps(params)
        ret = _mixin.decode_pledgeNode(params)
        ret = json.loads(ret)
        if 'error' in ret:
            raise Exception(ret['error'])
        return ret['data']
