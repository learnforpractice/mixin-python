"""
Mixin Python3 Websocket SDK
base on https://github.com/myrual/mixin_client_demo/blob/master/home_of_cnb_robot.py
code by Lee.c
update at 2018.12.2
"""
import json
import uuid
import gzip
import time
from io import BytesIO
import base64
import websockets

from pymixin import mixin_config
from pymixin.mixin_bot_api import MixinBotApi
from pymixin import log

logger = log.get_logger(__name__)

class MixinWSApi:

    def __init__(self, bot_config, on_message):
        self.bot = MixinBotApi(bot_config)
        self.ws = None
        self.on_message = on_message

    async def connect(self):
        if self.ws:
            return

        encoded = self.bot.gen_get_jwt_token('/', "", str(uuid.uuid4()))

        uri = "wss://blaze.mixin.one"
        #uri = 'wss://echo.websocket.org'
        headers={"Authorization": "Bearer " + encoded}
        self.ws = await websockets.connect(uri, subprotocols=["Mixin-Blaze-1"], extra_headers=headers)

    """
    run websocket server forever
    """
    async def run(self):
        while True:
            await self.connect()

            Message = {"id": str(uuid.uuid1()), "action": "LIST_PENDING_MESSAGES"}
            Message_instring = json.dumps(Message)

            fgz = BytesIO()
            gzip_obj = gzip.GzipFile(mode='wb', fileobj=fgz)
            gzip_obj.write(Message_instring.encode())
            gzip_obj.close()

            await self.ws.send(fgz.getvalue())
            while True:
                if not self.ws:
                    return
                try:
                    msg = await self.ws.recv()
                except websockets.exceptions.ConnectionClosedError:
                    self.ws = None
                    break
                except websockets.exceptions.ConnectionClosedOK:
                    return
                msg = BytesIO(msg)
                msg = gzip.GzipFile(mode="rb", fileobj=msg)
                msg = msg.read()
                msg = json.loads(msg)
                await self.on_message(msg)

    """
    =================
    REPLY USER METHOD
    =================
    """

    """
    generate a standard message base on Mixin Messenger format
    """


    async def writeMessage(self, action, params):

        message = {"id": str(uuid.uuid1()), "action": action, "params": params}
        message_instring = json.dumps(message)

        fgz = BytesIO()
        gzip_obj = gzip.GzipFile(mode='wb', fileobj=fgz)
        gzip_obj.write(message_instring.encode())
        gzip_obj.close()
        await self.ws.send(fgz.getvalue())

    """
    when receive a message, must reply to server
    ACKNOWLEDGE_MESSAGE_RECEIPT ack server received message
    """

    async def echoMessage(self, msgid):
        parameter4IncomingMsg = {"message_id": msgid, "status": "READ"}
        Message = {"id": str(uuid.uuid1()), "action": "ACKNOWLEDGE_MESSAGE_RECEIPT", "params": parameter4IncomingMsg}
        Message_instring = json.dumps(Message)
        fgz = BytesIO()
        gzip_obj = gzip.GzipFile(mode='wb', fileobj=fgz)
        gzip_obj.write(Message_instring.encode())
        gzip_obj.close()
        await self.ws.send(fgz.getvalue())
        return

    """
    reply a button to user
    """

    async def sendUserAppButton(self, in_conversation_id, to_user_id, realLink, text4Link, colorOfLink="#0084ff"):

        btn = '[{"label":"' + text4Link + '","action":"' + realLink + '","color":"' + colorOfLink + '"}]'

        btn = base64.b64encode(btn.encode('utf-8')).decode(encoding='utf-8')

        params = {"conversation_id": in_conversation_id, "recipient_id": to_user_id, "message_id": str(uuid.uuid4()),
                  "category": "PLAIN_TEXT", "data": btn}
        return await self.writeMessage("CREATE_MESSAGE", params)

    """
    reply a contact card to user
    """


    async def sendUserContactCard(self, in_conversation_id, to_user_id, to_share_userid):

        btnJson = json.dumps({"user_id": to_share_userid})
        btnJson = base64.b64encode(btnJson.encode('utf-8')).decode('utf-8')
        params = {"conversation_id": in_conversation_id, "recipient_id": to_user_id, "message_id": str(uuid.uuid4()),
                  "category": "PLAIN_CONTACT", "data": btnJson}
        return await self.writeMessage("CREATE_MESSAGE", params)

    """
    reply a text to user
    """

    async def sendUserText(self, in_conversation_id, to_user_id, textContent):

        textContent = textContent.encode('utf-8')
        textContent = base64.b64encode(textContent).decode(encoding='utf-8')

        params = {"conversation_id": in_conversation_id, "recipient_id": to_user_id, "status": "SENT",
                  "message_id": str(uuid.uuid4()), "category": "PLAIN_TEXT",
                  "data": textContent}
        return await self.writeMessage("CREATE_MESSAGE", params)

    """
    send user a pay button
    """
    async def sendUserPayAppButton(self, in_conversation_id, to_user_id, inAssetName, inAssetID, inPayAmount, linkColor="#0CAAF5"):
        payLink = "https://mixin.one/pay?recipient=" + mixin_config.client_id + "&asset=" + inAssetID + "&amount=" + str(
            inPayAmount) + '&trace=' + str(uuid.uuid1()) + '&memo=PRS2CNB'
        btn = '[{"label":"' + inAssetName + '","action":"' + payLink + '","color":"' + linkColor + '"}]'

        btn = base64.b64encode(btn.encode('utf-8')).decode(encoding='utf-8')

        gameEntranceParams = {"conversation_id": in_conversation_id, "recipient_id": to_user_id,
                              "message_id": str(uuid.uuid4()), "category": "PLAIN_TEXT", "data": btn}
        return await self.writeMessage("CREATE_MESSAGE", gameEntranceParams)

    async def sendAppCard(self, in_conversation_id, to_user_id, asset_id, amount, icon_url, title, description, color="#0080FF", memo=""):
        payLink = "https://mixin.one/pay?recipient=" + to_user_id + "&asset=" + asset_id + "&amount=" + \
                amount + "&trace=" + str(uuid.uuid4()) + "&memo="
        card =  '{"icon_url":"' + icon_url + '","title":"' + title + \
                '","description":"' + description + '","action":"'+ payLink + '"}'
        enCard = base64.b64encode(card.encode('utf-8')).decode(encoding='utf-8')
        params = {"conversation_id": in_conversation_id,  "message_id": str(uuid.uuid4()),
                  "category": "APP_CARD", "status": "SENT", "data": enCard}
        return await self.writeMessage("CREATE_MESSAGE", params)

    async def sendAppButtonGroup(self, in_conversation_id, to_user_id, buttons):
        buttonsStr = '[' + ','.join(str(btn) for btn in buttons) +']'
        enButtons = base64.b64encode(buttonsStr.encode('utf-8')).decode(encoding='utf-8')
        params = {"conversation_id": in_conversation_id,  "recipient_id": to_user_id,
                "message_id": str(uuid.uuid4()),
                "category": "APP_BUTTON_GROUP", "status": "SENT", "data": enButtons}
        return await self.writeMessage("CREATE_MESSAGE", params)

    def packButton(to_user_id, asset_id, amount, label, color="#FF8000", memo=""):
        payLink = "https://mixin.one/pay?recipient=" + to_user_id + "&asset=" + asset_id + "&amount=" + \
                    amount + "&trace=" + str(uuid.uuid4()) + "&memo="
        button  = '{"label":"' + label + '","color":"' + color + '","action":"' + payLink + '"}'
        return button
