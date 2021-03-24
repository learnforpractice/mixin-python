# MixinApi

## create_address

```python
from mixin.mixin_api import MixinApi
api = MixinApi('http://mixin-node0.exinpool.com:8239')
addr = api.create_address()
print(addr)
```

## get_info

```python
async def get_info(self)
```

```python
from mixin.mixin_api import MixinApi

api = MixinApi('http://mixin-node0.exinpool.com:8239')

info = await api.get_info()
print(info)
```

## sign_transaction

```python
def sign_transaction(self, trx, accounts, input_indexes=[0], seed='')
```

Example

```python
from mixin.testnet import MixinTestnet
from mixin.mixin_api import MixinApi

api = MixinApi('http://127.0.0.1:8001')

testnet = MixinTestnet()
testnet.start()
deposit_hash = await testnet.deposit()
await api.wait_for_transaction(deposit_hash)

account = {
    'address': 'XINFrqT5x74BVvtgLJEVhRhFc1GdJ3vmwiu7zJHVg7qjYvzx9wG7j1sENkXV7NfN9tQm1SsRNces7tcrxFas9nkr5H1B7HTm',
    'view_key': 'bd1a337f2319d502eb062a433cb79cf8e2daadd6bcd0bb2a21d4b073549cb30c',
    'spend_key': 'bd449970bdb5cf9afaf1f9c574a94f06ff7a0d3af0d9387867e1ba7e9193eb03'
}

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
        "amount": "100",
        "accounts": [account['address']],
        "script": "fffe01",
        "type": 0
        }
    ]
}

ret = api.sign_transaction(trx, [account])
print(ret['raw'])
print(ret['signatures'])

testnet.stop()
```

## send_raw_transaction
```python
async def send_raw_transaction(self, raw)
```

Example

```python
from mixin.testnet import MixinTestnet
from mixin.mixin_api import MixinApi

api = MixinApi('http://127.0.0.1:8001')

testnet = MixinTestnet()
testnet.start()
deposit_hash = await testnet.deposit()
await api.wait_for_transaction(deposit_hash)

account = {
    'address': 'XINFrqT5x74BVvtgLJEVhRhFc1GdJ3vmwiu7zJHVg7qjYvzx9wG7j1sENkXV7NfN9tQm1SsRNces7tcrxFas9nkr5H1B7HTm',
    'view_key': 'bd1a337f2319d502eb062a433cb79cf8e2daadd6bcd0bb2a21d4b073549cb30c',
    'spend_key': 'bd449970bdb5cf9afaf1f9c574a94f06ff7a0d3af0d9387867e1ba7e9193eb03'
}

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
        "amount": "100",
        "accounts": [account['address']],
        "script": "fffe01",
        "type": 0
        }
    ]
}

ret = api.sign_transaction(trx, [account])
print(ret['raw'])
print(ret['signatures'])
ret = await api.send_raw_transaction(ret['raw'])

testnet.stop()

```

## send_transaction

```python
async def send_transaction(self, trx, accounts, seed='')
```

```python
from mixin.testnet import MixinTestnet
from mixin.mixin_api import MixinApi

api = MixinApi('http://127.0.0.1:8001')

testnet = MixinTestnet()
testnet.start()
deposit_hash = await testnet.deposit()
await api.wait_for_transaction(deposit_hash)

account = {
    'address': 'XINFrqT5x74BVvtgLJEVhRhFc1GdJ3vmwiu7zJHVg7qjYvzx9wG7j1sENkXV7NfN9tQm1SsRNces7tcrxFas9nkr5H1B7HTm',
    'view_key': 'bd1a337f2319d502eb062a433cb79cf8e2daadd6bcd0bb2a21d4b073549cb30c',
    'spend_key': 'bd449970bdb5cf9afaf1f9c574a94f06ff7a0d3af0d9387867e1ba7e9193eb03'
}

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
        "amount": "100",
        "accounts": [account['address']],
        "script": "fffe01",
        "type": 0
        }
    ]
}

ret = await api.send_transaction(trx, [account])
print(ret['hash'])

testnet.stop()

```

## wait_for_transaction

```python
async def wait_for_transaction(self, _hash, max_time=30.0)
```

Example

[See send_transaction](#send_transaction)

## get_transaction
```python
async def get_transaction(self, trx_hash)
```

## decode_transaction

```python
def decode_transaction(self, raw)
```

```python
raw = '77770002a99c2e0e2b1da4d648755ef19bd95139acbbe6564cfb06dec7cd34931ca72cdc000100000000000000000000000000000000000000000000000000000000000000000000000077778dd50817c082cdcdd6f167514928767a4b52426997bd6d4930eca101c5ff8a27002a30786139373463373039636662343536363638363535336132303739303638356134376163656161333300423078346362353831323831663731313537303663356536663636393337313537346266646561333137333235653135656566333263643335366466306434373838620000000000000000000502540be400000000010000000502540be40000010427b4c98d89f614139f64024c862fb60b96b8831bb507572fbdc9e9da34d5174da4c1303f4dd749fdf63747df9e6037ff7412237f1342511a139d81a35abb4d0003fffe0100000000000100010000c0785ff67c651bd19b978aa44ffbb5fab0efe44fb1520d79d481f5cfe293efebd289af9200318bafbed69fe5ce164dfaff0764488d5bdd61a53f6addf4b07e07'
api = MixinApi('http://mixin-node0.exinpool.com:8239')
ret = api.decode_transaction(raw)
print(ret)
```
outputs:
```python
{'asset': 'a99c2e0e2b1da4d648755ef19bd95139acbbe6564cfb06dec7cd34931ca72cdc', 'extra': '', 'hash': 'e057fb4b044112f9ddb699128a77394f0f9f6cf39b7f9b2009c4431059143223', 'inputs': [{'deposit': {'Chain': '8dd50817c082cdcdd6f167514928767a4b52426997bd6d4930eca101c5ff8a27', 'AssetKey': '0xa974c709cfb4566686553a20790685a47aceaa33', 'TransactionHash': '0x4cb581281f7115706c5e6f669371574bfdea317325e15eef32cd356df0d4788b', 'OutputIndex': 0, 'Amount': '100.00000000'}}], 'outputs': [{'amount': '100.00000000', 'keys': ['0427b4c98d89f614139f64024c862fb60b96b8831bb507572fbdc9e9da34d517'], 'mask': '4da4c1303f4dd749fdf63747df9e6037ff7412237f1342511a139d81a35abb4d', 'script': 'fffe01', 'type': 0}], 'signatures': [{'0': 'c0785ff67c651bd19b978aa44ffbb5fab0efe44fb1520d79d481f5cfe293efebd289af9200318bafbed69fe5ce164dfaff0764488d5bdd61a53f6addf4b07e07'}], 'version': 2}
```

## get_asset_id
```python
def get_asset_id(self, chain_id, asset_key)
```

```python
api = MixinApi('http://mixin-node0.exinpool.com:8239')
chain_id = '8dd50817c082cdcdd6f167514928767a4b52426997bd6d4930eca101c5ff8a27'
contract_address = '0xa974c709cfb4566686553a20790685a47aceaa33'
ret = api.get_asset_id(chain_id, contract_address)
print(ret)
```

## get_eth_asset_id
```python
def get_eth_asset_id(self, contract_address)
```

```python
api = MixinApi('http://mixin-node0.exinpool.com:8239')
contract_address = '0xa974c709cfb4566686553a20790685a47aceaa33'
ret = api.get_eth_asset_id(contract_address)
print(ret)
#output: a99c2e0e2b1da4d648755ef19bd95139acbbe6564cfb06dec7cd34931ca72cdc
```

## get_eos_asset_id
```python
def get_eos_asset_id(self, contract, symbol)
```


```python
api = MixinApi('http://mixin-node0.exinpool.com:8239')
ret = api.get_eos_asset_id('eosio.token', 'EOS')
print(ret)
# output : 6ac4cbffda9952e7f0d924e4cfb6beb29d21854ac00bfbf749f086302d0f7e5d
```

## get_public_key
```python
def get_public_key(self, private_key)
```

## decode_address
```python
def decode_address(self, addr)
```

## get_utxo
```python
async def get_utxo(self, hash, index)
```

## new_ghost_keys
```python
def new_ghost_keys(self, seed, accounts, output_index)
```

## sign_message
```python
def sign_message(self, key, msg)
```

## verify_signature
```python
def verify_signature(self, msg, pub, sig)
```

## batch_verify
```python
def batch_verify(self, msg, keys, sigs)
```
