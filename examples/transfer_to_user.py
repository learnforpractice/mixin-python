import json
import uuid
import asyncio
from pymixin.mixin_bot_api import MixinBotApi

#path to bot config
bot_config_file = 'test1.json'
with open(bot_config_file, 'r') as f:
    bot_config = f.read()
    bot_config = json.loads(bot_config)

mixin_bot = MixinBotApi(bot_config)

user_id = 'e0148fc6-0e10-470e-8127-166e0829c839'
asset_id = '965e5c6e-434c-3fa9-b780-c50f43cd955c' #(CNB)

async def run():
    r = await mixin_bot.transfer_to_user(user_id, asset_id, 0.00000006, 'hello')
    print(r)
    await mixin_bot.close()
asyncio.run(run())
