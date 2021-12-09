import os
import json
import time
import asyncio
import httpx

from .import log
from . import _mixin

logger = log.get_logger(__name__)

ETH_CHAIN_ID = '8dd50817c082cdcdd6f167514928767a4b52426997bd6d4930eca101c5ff8a27'
EOS_CHAIN_ID = '6ac4cbffda9952e7f0d924e4cfb6beb29d21854ac00bfbf749f086302d0f7e5d'

def check_result(ret):
    if 'error' in ret:
        raise Exception(ret['error'])
    return json.loads(ret['data'])

def encrypt_ed25519_pin(pin, pinTokenBase64, sessionId, privateKey, interator):
    ret = _mixin.encrypt_ed25519_pin(pin, pinTokenBase64, sessionId, privateKey, interator)
    ret = json.loads(ret)
    if 'error' in ret:
        raise Exception(ret['error'])
    return ret['data']

class MixinApi(object):

    def __init__(self, url='http://127.0.0.1:8001'):
        self.node_url = url
        self.client = httpx.AsyncClient()
        self.init()

    def init(self):
        _mixin.init()

    def set_node(self, url):
        self.node_url = url

    def get_mixin_version(self):
        return _mixin.get_mixin_version()

    def create_address(self, spend_key="", view_key="", public=False):
        params = {
            "view_key": view_key,
            "spend_key": spend_key,
            "public": public
        }
        ret = _mixin.create_address(json.dumps(params))
        ret = json.loads(ret)
        if 'error' in ret:
            raise Exception(ret['error'])
        return ret['data']

    def get_public_key(self, private_key):
        ret = _mixin.get_public_key(private_key)
        ret = json.loads(ret)
        if 'error' in ret:
            raise Exception(ret['error'])
        return ret['data']

    def generate_random_seed(self):
        return _mixin.generate_random_seed()

    def decode_address(self, addr):
        '''
        Example:
        from pymixin.mixin_api import MixinApi
        api = MixinApi('http://mixin-node0.exinpool.com:8239')
        address = api.create_address()
        addr = address['address']
        r = api.decode_address(addr)
        print(r)
        '''
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
        key = json.dumps(key)
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

    def encode_transaction(self, trx, signs=[]):
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

    def sign_transaction(self, trx, accounts, input_indexes=[0], seed=''):
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
            "keys"
        }
        '''

        keys = []
        for a in accounts:
            keys.append(a['view_key'] + a['spend_key'])

        params = {
            "seed": seed,
            "keys": keys,
            "raw": trx,
            "input_indexes": input_indexes
        }

        params["node"] = self.node_url
        params = json.dumps(params)

        ret = _mixin.sign_transaction(params)
        ret = json.loads(ret)
        if 'error' in ret:
            raise Exception(ret['error'])
        ret = ret['data']
        ret['signatures'] = json.loads(ret['signatures'])
        return ret

    async def send_raw_transaction(self, raw):
        data = {'method': 'sendrawtransaction', 'params': [raw]}
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        r = await self.client.post(self.node_url, json=data, headers=headers)
        r = r.json()
        if 'error' in r:
            raise Exception(r['error'])
        return r['data']

    async def send_transaction(self, trx, accounts, seed=''):
        input_indexes = [i for i in range(len(trx['inputs']))]
        r = self.sign_transaction(trx, accounts, input_indexes, seed)
        return await self.send_raw_transaction(r['raw'])

    async def wait_for_transaction(self, _hash, max_time=30.0):
        end = time.monotonic() + max_time
        while True:
            if end <= time.monotonic():
                raise Exception('wait timeout!')

            r = await self.get_transaction(_hash)
            if not r:
                await asyncio.sleep(0.1)
                continue
            if 'snapshot' in r:
                return r

    async def get_info(self):
        data = {'method': 'getinfo', 'params': []}
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        r = await self.client.post(self.node_url, json=data, headers=headers)
        r = r.json()
        if 'error' in r:
            raise Exception(r['error'])
        return r['data']

    async def list_all_nodes(self, threshold, state):
        data = {'method': 'listallnodes', 'params': [threshold, state]}
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        r = await self.client.post(self.node_url, json=data, headers=headers)
        r = r.json()
        if 'error' in r:
            raise Exception(r['error'])
        return r['data']

    async def get_utxo(self, hash, index):
        data = {'method': 'getutxo', 'params': [hash, index]}
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        r = await self.client.post(self.node_url, json=data, headers=headers)
        r = r.json()
        if 'error' in r:
            raise Exception(r['error'])
        return r['data']

    async def get_cache_transaction(self, _hash):
        data = {'method': 'getcachetransaction', 'params': [_hash]}
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        r = await self.client.post(self.node_url, json=data, headers=headers)
        r = r.json()
        if 'error' in r:
            raise Exception(r['error'])
        return r['data']

    async def get_snapshot(self, _hash):
        data = {'method': 'getsnapshot', 'params': [_hash]}
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        r = await self.client.post(self.node_url, json=data, headers=headers)
        r = r.json()
        if 'error' in r:
            raise Exception(r['error'])
        return r['data']

    async def list_mint_works(self, offset):
        data = {'method': 'listmintworks', 'params': [offset]}
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        r = await self.client.post(self.node_url, json=data, headers=headers)
        r = r.json()
        if 'error' in r:
            raise Exception(r['error'])
        return r['data']

    async def list_mint_distributions(self, offset, count, tx):
        data = {'method': 'listmintdistributions', 'params': [offset, count, tx]}
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        r = await self.client.post(self.node_url, json=data, headers=headers)
        r = r.json()
        if 'error' in r:
            raise Exception(r['error'])
        return r['data']

    async def get_round_by_number(self, node, num):
        data = {'method': 'getroundbynumber', 'params': [node, num]}
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        r = await self.client.post(self.node_url, json=data, headers=headers)
        r = r.json()
        if 'error' in r:
            raise Exception(r['error'])
        return r['data']

    async def get_transaction(self, trx_hash):
        data = {'method': 'gettransaction', 'params': [trx_hash]}
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        r = await self.client.post(self.node_url, json=data, headers=headers)
        r = r.json()
        if 'error' in r:
            raise Exception(r['error'])
        return r['data']

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

    def sign_message(self, private_key, msg):
        ret = _mixin.sign_message(private_key, msg)
        ret = json.loads(ret)
        if 'error' in ret:
            raise Exception(ret['error'])
        return ret['data']

    def verify_signature(self, msg, pub, sig):
        ret = _mixin.verify_signature(msg, pub, sig)
        ret = json.loads(ret)
        if 'error' in ret:
            raise Exception(ret['error'])
        return ret['data']

    def batch_verify(self, msg, keys, sigs):
        return _mixin.batch_verify(msg, keys, sigs)

    def get_asset_id(self, chain_id, asset_key):
        '''
        Example:
        api = MixinApi('http://mixin-node0.exinpool.com:8239')
        chain_id = '8dd50817c082cdcdd6f167514928767a4b52426997bd6d4930eca101c5ff8a27'
        asset_key = '0xa974c709cfb4566686553a20790685a47aceaa33'
        ret = api.get_asset_id(chain_id, asset_key)
        '''
        asset = {
            'chain_id': chain_id,
            'asset_key': asset_key
        }
        asset = json.dumps(asset)
        ret = _mixin.get_asset_id(asset)
        ret = json.loads(ret)
        if 'error' in ret:
            raise Exception(ret['error'])
        return ret['data']

    def get_eth_asset_id(self, contract_address):
        return self.get_asset_id(ETH_CHAIN_ID, contract_address)

    def get_eos_asset_id(self, contract, symbol):
        asset_key = f'{contract}:{symbol}'
        return self.get_asset_id(EOS_CHAIN_ID, asset_key)

    def get_fee_asset_id(self, chain_id, asset_key):
        asset = {
            'chain_id': chain_id,
            'asset_key': asset_key
        }
        asset = json.dumps(asset)
        ret = _mixin.get_fee_asset_id(asset)
        ret = json.loads(ret)
        if 'error' in ret:
            raise Exception(ret['error'])
        return ret['data']

    def new_ghost_keys(self, seed, accounts, output_index):
        if isinstance(seed, bytes):
            seed = seed.hex()
        # assert len(seed) == 64, 'bad seed length'
        accounts = json.dumps(accounts)
        ret = _mixin.new_ghost_keys(seed, accounts, output_index)
        ret = json.loads(ret)
        if 'error' in ret:
            raise Exception(ret['error'])
        return json.loads(ret['data'])

    async def get_top_tokens(self):
        ret = await self.client.get('/network/assets/top')
        return check_result(ret)
