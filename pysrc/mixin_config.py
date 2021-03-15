# -*- coding: utf-8 -*-

#helloworld

"""
Mixin Config
get below config from 'https://developers.mixin.one/dashboard'
code by lee.c
update at 2018.12.2
"""
import os
import sys
import json
import importlib

try:
    index = sys.argv.index('--config')
    config = os.path.join('configs', sys.argv[index + 1])
except ValueError:
    config = 'configs/mixin_config_helloworld.json'

if not os.path.exists(config):
    client_id = ''
    client_secret = ''
    pay_pin = ''
    pay_session_id = ''
    pin_token = ''
    private_key = ''
else:
    with open(config, 'r') as f:
        config = f.read()
    config = json.loads(config)

    client_id = config['client_id']
    client_secret = config['client_secret']
    pay_pin = config['pin']
    pay_session_id = config['session_id']
    pin_token = config['pin_token']
    private_key = config['private_key']

receivers = [
    "e07c06fa-084c-4ce1-b14a-66a9cb147b9e",
    "e0148fc6-0e10-470e-8127-166e0829c839",
    "3e72ca0c-1bab-49ad-aa0a-4d8471d375e7"
]
