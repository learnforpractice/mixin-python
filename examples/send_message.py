import sys
import json
import uuid
import asyncio
from pymixin.mixin_bot_api import MixinBotApi

#path to bot config
bot_config_file = sys.argv[1]
with open(bot_config_file, 'r') as f:
    bot_config = f.read()
    bot_config = json.loads(bot_config)

mixin_bot = MixinBotApi(bot_config)

user_id = 'e0148fc6-0e10-470e-8127-166e0829c839'
asset_id = '965e5c6e-434c-3fa9-b780-c50f43cd955c' #(CNB)

async def run():
    conversation_id = '80f5c80c-e5b2-309e-ba18-196ff57d540f'

    await mixin_bot.send_text_message(conversation_id, 'hello, world')

    name = "jiayou"
    album_id = "fb0eea56-c09f-4372-8ff4-9799f15b0f03"
    sticker_id = "0083ea85-7d28-4d0e-8132-427b6c3c9507"
    await mixin_bot.send_sticker_message(conversation_id, name, album_id, sticker_id)

    await mixin_bot.send_contract_message(conversation_id, user_id)

    label = 'hello'
    color = "#d53120"
    action = 'https://mixin.one'
    await mixin_bot.send_button_group_message(conversation_id, label, color, action)

    amount = 0.00000006
    trace_id = str(uuid.uuid1())
    label = 'pay fee'
    color = "#d53120"
    action = f"https://mixin.one/pay?recipient={bot_config['client_id']}&asset={asset_id}&amount={amount:.8f}&trace={trace_id}&memo=hello"
    print(action)
    await mixin_bot.send_button_group_message(conversation_id, label, color, action)

    await mixin_bot.close()
asyncio.run(run())
