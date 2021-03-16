import os
import json
import shutil
import tempfile
import shlex, subprocess

from .mixin_api import MixinApi
from . import log

logger = log.get_logger(__name__)

class MixinTestnet(object):

    def __init__(self):
        self.api = MixinApi('')
        self.genesis = None
        self.node_addresses = None
        self.config_dirs = None
        self.nodes = []

    def create_test_genesis(self):
        genesis = {
        "domains": [
            {
            "balance": "50000",
            "signer": ""
            }
        ],
        "epoch": 1615788541,
        "nodes": []
        }

        node_addresses = []
        for i in range(7):
            payee = self.api.create_address(public=True)
            signer = self.api.create_address(public=True)
            args = {
                'payee': payee,
                'signer': signer
            }
            node_addresses.append(args)

        genesis['domains'][0]['signer'] = node_addresses[0]['signer']['address']

        for i in range(7):
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
        for i in range(7):
            port = 7001+i
            node = {
                "host": f"127.0.0.1:{port}",
                "signer": self.node_addresses[i]['signer']['address']
            }
            nodes.append(node)

        nodes = json.dumps(nodes, indent=' ')

        self.config_dirs = []
        if not os.path.exists('testnet'):
            os.mkdir('testnet')
        for i in range(7):
            port = 7001+i
            config = '''
[node]
signer-key = "%s"
consensus-only = true
memory-cache-size = 128
cache-ttl = 3600
ring-cache-size = 4096
ring-final-size = 16384
[network]
listener = "127.0.0.1:%s" 
            '''%(self.node_addresses[i]['signer']['view_key'], port)

            temp_dir = os.path.join('testnet', f'config-{port}')
            os.mkdir(temp_dir)

            self.config_dirs.append(temp_dir)

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
        with open('testnet/testnet.json', 'w') as f:
            testnet_config = json.dumps(testnet_config, indent=' ')
            f.write(testnet_config)

    def _start(self):
        if self.nodes:
            raise Exception('testnet is running')

        for i in range(7):
            port = 7001+i
            config_dir = self.config_dirs[i]
            cmd = f'python3 -m mixin.main kernel -dir {config_dir} -port {port}'
            args = shlex.split(cmd)
            p = subprocess.Popen(args, stdout=subprocess.PIPE)
            self.nodes.append(p)

    def start(self):
        if os.path.exists('testnet/testnet.json'):
            return self.restart('testnet/testnet.json')
        self._create()
        self._start()

    def restart(self, testnet_config_file='testnet/testnet.json'):
        with open(testnet_config_file, 'r') as f:
            testnet_config = f.read()
            testnet_config = json.loads(testnet_config)

            self.node_addresses=testnet_config["node_addresses"]
            self.config_dirs=testnet_config["config_dirs"]
        self._start()

    def shutdown(self, cleanup=False):
        for p in self.nodes:
            p.kill()

        if cleanup:
            if os.path.exists('testnet/testnet.json'):
                os.remove('testnet/testnet.json')
 
            if self.config_dirs:
                for d in self.config_dirs:
                    shutil.rmtree(d)
                self.config_dirs = None
        self.nodes = []
