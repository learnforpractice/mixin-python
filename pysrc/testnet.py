import os
import json
import time
import asyncio
import signal
import shutil
import tempfile
import requests
import shlex, subprocess
from subprocess import Popen, PIPE


from .mixin_api import MixinApi
from . import log

logger = log.get_logger(__name__)

class MixinTestnet(object):

    def __init__(self, node_count=7):
        self.api = MixinApi('http://127.0.0.1:8001')
        self.genesis = None
        self.node_addresses = None
        self.config_dirs = None
        self.deposit_hash = None
        self.nodes = []
        self.node_count = node_count

        self.test_account = {
            'address': 'XINFrqT5x74BVvtgLJEVhRhFc1GdJ3vmwiu7zJHVg7qjYvzx9wG7j1sENkXV7NfN9tQm1SsRNces7tcrxFas9nkr5H1B7HTm',
            'view_key': 'bd1a337f2319d502eb062a433cb79cf8e2daadd6bcd0bb2a21d4b073549cb30c',
            'spend_key': 'bd449970bdb5cf9afaf1f9c574a94f06ff7a0d3af0d9387867e1ba7e9193eb03'
        }

        self.test_account2 = {
            'address': 'XINHJLCRBWJ3AgcrNhKppVMvjinapzumLVL253opKzs6Jk5bUBHWKH6paPr2exhwqYZ3FcPtbnitJMF6TXk8UcEx8u2nUt4S',
            'view_key': 'fae95f3dfaf0a7b2f4ca95d6ed94f8002492875e018000f786284be1beacf10c',
            'spend_key': '0ff0016d98026b21df80f4b1fe0db5fc460e7e66f47f67acfd773e5cc4fbb207'
        }

    def kill_all_nodes(self):
        for port in range(8001, 8008):
            self.kill_node(port)

    def kill_node(self, port):
        process = subprocess.Popen(["lsof", "-i", ":{0}".format(port)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        for process in stdout.decode("utf-8").split("\n")[1:]:
            if not '(LISTEN)' in process:
                continue
            data = [x for x in process.split(" ") if x != '']
            if (len(data) <= 1):
                continue
            os.kill(int(data[1]), signal.SIGKILL)

    def create_test_genesis(self):
        genesis = {
        "domains": [
            {
            "balance": "50000",
            "signer": ""
            }
        ],
        "epoch": int(time.time()),
        "nodes": []
        }

        node_addresses = []
        for i in range(self.node_count):
            payee = self.api.create_address(public=True)
            signer = self.api.create_address(public=True)
            args = {
                'payee': payee,
                'signer': signer
            }
            node_addresses.append(args)

        genesis['domains'][0]['signer'] = node_addresses[0]['signer']['address']

        for i in range(self.node_count):
            node = {
            "balance": "10000",
            "payee": node_addresses[i]['payee']['address'],
            "signer": node_addresses[i]['signer']['address']
            }
            genesis['nodes'].append(node)

        return genesis, node_addresses

    def _create(self):
        self.genesis, self.node_addresses = self.create_test_genesis()

        genesis = json.dumps(self.genesis, indent=' ')
        nodes = []
        for i in range(self.node_count):
            port = 7001+i
            node = {
                "host": f"127.0.0.1:{port}",
                "signer": self.node_addresses[i]['signer']['address']
            }
            nodes.append(node)

        nodes = json.dumps(nodes, indent=' ')

        self.config_dirs = []
        if not os.path.exists('.testnet'):
            os.mkdir('.testnet')
        for i in range(self.node_count):
            port = 7001+i
            temp_dir = os.path.join('.testnet', f'config-{port}')
            self.config_dirs.append(temp_dir)
            if os.path.exists(temp_dir):
                continue
            os.mkdir(temp_dir)

            config = '''
[node]
signer-key = "%s"
consensus-only = true
memory-cache-size = 128
cache-ttl = 3600
ring-cache-size = 4096
ring-final-size = 16384
[network]
listener = "127.0.0.1:%s"'''%(self.node_addresses[i]['signer']['spend_key'], port)

            config_file = os.path.join(temp_dir, 'config.toml')
            with open(config_file, 'w') as f:
                f.write(config)

            genesis_file = os.path.join(temp_dir, 'genesis.json')
            with open(genesis_file, 'w') as f:
                f.write(genesis)

            nodes_file = os.path.join(temp_dir, 'nodes.json')
            with open(nodes_file, 'w') as f:
                f.write(nodes)

        testnet_config = dict(
            node_addresses=self.node_addresses,
            config_dirs=self.config_dirs
        )
        with open('.testnet/testnet.json', 'w') as f:
            testnet_config = json.dumps(testnet_config, indent=' ')
            f.write(testnet_config)

    def _start(self):
        if self.nodes:
            raise Exception('testnet is running')

        for i in range(self.node_count):
            port = 7001+i
            config_dir = self.config_dirs[i]
            cmd = f'python3 -m pymixin.main kernel -dir {config_dir} -port {port}'
            args = shlex.split(cmd)
            log = open(f'{config_dir}/log.txt', 'a')
            p = subprocess.Popen(args, stdout=log, stderr=log)
            self.nodes.append(p)

        time.sleep(1.5)
        while True:
            try:
                data = {'method': 'getinfo', 'params': []}
                headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
                r = requests.post('http://127.0.0.1:8007', json=data, headers=headers)
                r = r.json()
                break
            except Exception as e:
                print(e)
                time.sleep(0.5)

    def remove_all_config_dirs(self):
        self.config_dirs = []
        for port in range(7001, 7008):
            temp_dir = os.path.join('.testnet', f'config-{port}')
            self.config_dirs.append(temp_dir)
        self.cleanup()

    def start(self, new_testnet=True):
        if new_testnet:
            self.kill_all_nodes()
            if os.path.exists('.testnet'):
                shutil.rmtree('.testnet')

        if os.path.exists('.testnet/testnet.json'):
            return self.restart('.testnet/testnet.json')
        self._create()
        self._start()

    def restart(self, testnet_config_file='.testnet/testnet.json'):
        with open(testnet_config_file, 'r') as f:
            testnet_config = f.read()
            testnet_config = json.loads(testnet_config)

            self.node_addresses=testnet_config["node_addresses"]
            self.config_dirs=testnet_config["config_dirs"]
        self._start()

    async def deposit(self):
        if self.deposit_hash:
            return self.deposit_hash

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
                "accounts": [self.test_account['address']],
                "script": "fffe01",
                "type": 0
                }
            ]
        }

        address = self.node_addresses[0]['signer']
        r = self.api.sign_transaction(trx, [address])
        r = await self.api.send_raw_transaction(r['raw'])
        logger.info('deposit hash %s', r['hash'])
        self.deposit_hash = r['hash']
        return r['hash']

    def cleanup(self):
        if os.path.exists('.testnet/testnet.json'):
            os.remove('.testnet/testnet.json')

        if self.config_dirs:
            for d in self.config_dirs:
                if os.path.exists(d):
                    shutil.rmtree(d)
            self.config_dirs = None
    
    def stop(self, cleanup=True):
        for p in self.nodes:
            p.kill()
        self.nodes = []

        if not cleanup:
            return

        self.cleanup()

    def __del__(self):
        self.stop()

