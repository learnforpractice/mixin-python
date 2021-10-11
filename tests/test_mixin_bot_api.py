import os
import json
import time
import pytest
import uuid
import httpx

from pymixin.mixin_bot_api import MixinBotApi
from pymixin import mixin_config
from pymixin import log

logger = log.get_logger(__name__)

class TestMixinApi(object):

    @classmethod
    def setup_class(cls):
        bot_config = '/Users/newworld/dev/mixin/mixin-python3-sdk/configs/mixin_config_helloworld4.json'
        with open(bot_config, 'r') as f:
            bot_config = f.read()
            bot_config = json.loads(bot_config)
        cls.mixin_bot = MixinBotApi(bot_config)

    @classmethod
    def teardown_class(cls):
        pass

    def setup_method(self, method):
        logger.warning('test start: %s', method.__name__)

    def teardown_method(self, method):
        pass

    @pytest.mark.asyncio
    async def test_ghost_key(self):
        hint = str(uuid.uuid4())
        hint = 'b65f5807-03b7-42bd-acff-a9242530fd18'
        hint = f'2021-05-14T14:22:58.838935Z{hint}'
        logger.info(hint)
        r = await self.mixin_bot.get_ghost_keys(['f32bb6ab-1a4d-44bb-892f-f0129239df89'], 0, hint)
        logger.info(r)

    @pytest.mark.asyncio
    async def test_send_message(self):
        conversation_id = "d91f020c-fa42-457c-b5d2-9243eda5f1bd"
        r = await self.mixin_bot.send_text_message(conversation_id, 'hello,world')
        logger.info(r)

