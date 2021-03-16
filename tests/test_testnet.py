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
import asyncio
import threading
from io import BytesIO
import httpx

from mixin.mixin_api import MixinApi
from mixin.mixin_bot_api import MixinBotApi
from mixin import mixin_config
from mixin import log
from mixin.testnet import MixinTestnet

logger = log.get_logger(__name__)

class TestMixinApi(object):

    @classmethod
    def setup_class(cls):
        cls.testnet = MixinTestnet()
        cls.testnet.start()
        cls.api = MixinApi('http://127.0.0.1:8001')

        loop = asyncio.get_event_loop()        
        async def wait():
            api = MixinApi('http://127.0.0.1:8007')
            await asyncio.sleep(0.5)
            while True:
                try:
                    await cls.api.get_info()
                    return
                except Exception as e:
                    await asyncio.sleep(0.5)
                    # logger.info(e)
        loop.run_until_complete(wait())

    @classmethod
    def teardown_class(cls):
        cls.testnet.shutdown(cleanup=True)

    def setup_method(self, method):
        logger.warning('test start: %s', method.__name__)

    def teardown_method(self, method):
        pass

    @pytest.mark.asyncio
    async def test_hello(self):
        info = await self.api.get_info()
        logger.info(json.dumps(info, indent=' '))
