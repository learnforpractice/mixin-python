# mixin api

## sign_transaction
```python
api = MixinApi('http://mixin-node0.exinpool.com:8239')

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

params = {
    "seed": '',
    "keys": [account['view_key'] + signer_key,],
    "raw": trx,
    "input_index": 0
}
await api.sign_transaction('', [account], trx, 0)
```
