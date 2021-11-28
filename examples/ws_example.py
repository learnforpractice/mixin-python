import sys
import json
import uuid
import asyncio
import base64
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(module)s %(lineno)d %(message)s')
logger = logging.getLogger(__name__)

from pymixin.mixin_bot_api import MixinBotApi
from pymixin.mixin_ws_api import MixinWSApi


bot_config = sys.argv[1]

with open(bot_config) as f:
    bot_config = f.read()
    bot_config = json.loads(bot_config)
    mixin_bot = MixinBotApi(bot_config)

async def on_message(message):
    logger.info(message)
    if 'error' in message:
        return
    action = message["action"]
    if action not in ["ACKNOWLEDGE_MESSAGE_RECEIPT", "CREATE_MESSAGE", "LIST_PENDING_MESSAGES"]:
        logger.info("unknow action %s", action)
        return

    if action == "ACKNOWLEDGE_MESSAGE_RECEIPT":
        return

    if not action == "CREATE_MESSAGE":
        return

    data = message["data"]
    msgid = data["message_id"]
    typeindata = data["type"]
    categoryindata = data["category"]
    user_id = data["user_id"]
    conversation_id = data["conversation_id"]

    created_at = data["created_at"]
    updated_at = data["updated_at"]

    await mixin_ws.echoMessage(msgid)

    logger.info('user_id %s', user_id)
    logger.info("created_at %s",created_at)

    if 'error' in message:
        return

    if not categoryindata in ["SYSTEM_ACCOUNT_SNAPSHOT", "PLAIN_TEXT", "SYSTEM_CONVERSATION", "PLAIN_STICKER", "PLAIN_IMAGE", "PLAIN_CONTACT"]:
        logger.info("unknow category:", categoryindata)
        return

    if not categoryindata == "PLAIN_TEXT" and typeindata == "message":
        return

    data = data["data"]
    logger.info(data)
    data = base64.b64decode(data)
    logger.info('++++on_message:cmd %s', data)
    data = base64.urlsafe_b64decode(data+b'===')
    logger.info(data)

mixin_ws = MixinWSApi(bot_config, on_message=on_message)

async def start():
    await mixin_ws.run()

if __name__ == '__main__':
    asyncio.run(start())
