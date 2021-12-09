import os
import sys
import json
import time
import pytest
import uuid
import httpx
import asyncio

from pymixin.mixin_bot_api import MixinBotApi
from pymixin import mixin_config
from pymixin import log

logger = log.get_logger(__name__)

bot_config = ''
if not bot_config:
    print('bot config file not specified')
    sys.exit(-1)

with open(bot_config, 'r') as f:
    bot_config = f.read()
    bot_config = json.loads(bot_config)
mixin_bot = MixinBotApi(bot_config)

async def start():
    hint = str(uuid.uuid4())
    r = await mixin_bot.verify_pin()
    print(r)
    # r = await mixin_bot.get_ghost_keys(['f32bb6ab-1a4d-44bb-892f-f0129239df89'], 0, hint)
    # print(r)

asyncio.run(start())