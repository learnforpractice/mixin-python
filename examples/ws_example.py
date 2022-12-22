import sys
import json
import uuid
import asyncio
import base64
import logging
from typing import Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(module)s %(lineno)d %(message)s')
logger = logging.getLogger(__name__)

from pymixin.mixin_ws_api import MixinWSApi, MessageView, Category, MessageStatus

bot_config = None

with open(sys.argv[1]) as f:
    bot_config = f.read()
    bot_config = json.loads(bot_config)


class MixinBot(MixinWSApi):
    def __init__(self):
        super().__init__(bot_config, on_message=self.on_message)

    async def on_message(self, id: str, action: str, msg: Optional[MessageView]) -> None:
        logger.info("on_message: %s %s %s", id, action, msg)

        if action not in ["ACKNOWLEDGE_MESSAGE_RECEIPT", "CREATE_MESSAGE", "LIST_PENDING_MESSAGES"]:
            logger.info("unknown action %s", action)
            return

        if action == "ACKNOWLEDGE_MESSAGE_RECEIPT":
            return

        if not action == "CREATE_MESSAGE":
            return

        if not msg:
            return

        msgid = msg.message_id
        created_at = msg.created_at
        updated_at = msg.updated_at

        await self.echoMessage(msgid)

        logger.info('user_id %s', msg.user_id)
        logger.info("created_at %s",created_at)

        if not msg.category in ["SYSTEM_ACCOUNT_SNAPSHOT", "PLAIN_TEXT", "SYSTEM_CONVERSATION", "PLAIN_STICKER", "PLAIN_IMAGE", "PLAIN_CONTACT"]:
            logger.info("unknown category: %s", msg.category)
            return

        if not msg.category == "PLAIN_TEXT" and msg.type == "message":
            return

        logger.info(msg.data)
        data = base64.urlsafe_b64decode(msg.data)
        logger.info(data)
        await self.sendUserText(msg.conversation_id, msg.user_id, data.decode())

bot = MixinBot()

async def start():
    await bot.run()

if __name__ == '__main__':
    asyncio.run(start())
