# -*- coding: utf-8 -*-
"""
Mixin API for Python 3.x
This SDK base on 'https://github.com/myrual/mixin_client_demo/blob/master/mixin_api.py'
some method note '?', because can't run right result, may be it will be resolved later.

env: python 3.x
code by lee.c
update at 2018.12.2
"""
from typing import Union, List
import time
import base64
import hashlib
import datetime
import uuid
import json

import jwt
import Crypto
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Signature import PKCS1_v1_5
from Crypto import Random
from Crypto.Cipher import AES
from urllib.parse import urlencode

from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization

from .message_types import ButtonMessage
from . import mixin_api

import httpx

class MixinBotApi:
    def __init__(self, mixin_config):

        # robot's config
        self.client_id = mixin_config['client_id']
        # self.client_secret = mixin_config['client_secret']
        self.pay_session_id = mixin_config['session_id']
        self.pay_pin = mixin_config['pin']
        self.pin_token = mixin_config['pin_token']
        self.private_key = mixin_config['private_key']
        self.private_key_base64 = self.private_key

        if self.private_key.find('RSA PRIVATE KEY') >= 0:
            self.algorithm='RS512'
        else:
            self.algorithm = 'EdDSA'
            self.private_key = self.decode_ed25519(self.private_key)

        self.client = httpx.AsyncClient()

        self.keyForAES = ""
        # mixin api base url
        self.api_base_url = 'https://api.mixin.one'
        #self.api_base_url = 'https://mixin-api.zeromesh.net'

    def decode_ed25519(cls, priv):
        if not len(priv) % 4 == 0:
            priv = priv + '===='
        priv = base64.b64decode(priv, altchars=b'-_')
        return ed25519.Ed25519PrivateKey.from_private_bytes(priv[:32])

    def generate_sig(self, method, uri, body):
        hashresult = hashlib.sha256((method + uri+body).encode('utf-8')).hexdigest()
        return hashresult

    def gen_get_post_sig(self, methodstring, uristring, bodystring):
        jwtSig = self.generate_sig(methodstring, uristring, bodystring)
        return jwtSig

    def gen_get_sig(self, uristring, bodystring):
        return self.gen_get_post_sig("GET", uristring, bodystring)

    def genPOSTSig(self, uristring, bodystring):
        return self.gen_get_post_sig("POST", uristring, bodystring)

    def gen_get_jwt_token(self, uristring, bodystring, jti):
        jwtSig = self.gen_get_sig(uristring, bodystring)
        iat = datetime.datetime.utcnow()
        exp = datetime.datetime.utcnow() + datetime.timedelta(seconds=200)
        encoded = jwt.encode({'uid':self.client_id, 'sid':self.pay_session_id,'iat':iat,'exp': exp, 'jti':jti,'sig':jwtSig}, self.private_key, algorithm=self.algorithm)

        return encoded

    def gen_get_listen_signed_token(self, uristring, bodystring, jti):
        jwtSig = self.gen_get_sig(uristring, bodystring)
        iat = datetime.datetime.utcnow()
        exp = datetime.datetime.utcnow() + datetime.timedelta(seconds=200)
        encoded = jwt.encode({'uid':self.client_id, 'sid':self.pay_session_id,'iat':iat,'exp': exp, 'jti':jti,'sig':jwtSig}, self.private_key, algorithm=self.algorithm)
        privKeyObj = RSA.importKey(self.private_key)
        signer = PKCS1_v1_5.new(privKeyObj)
        signature = signer.sign(encoded)
        return signature


    def gen_post_jwt_token(self, uristring, bodystring, jti):
        jwtSig = self.genPOSTSig(uristring, bodystring)
        iat = datetime.datetime.utcnow()
        exp = datetime.datetime.utcnow() + datetime.timedelta(seconds=200)
        encoded = jwt.encode({'uid':self.client_id, 'sid':self.pay_session_id,'iat':iat,'exp': exp, 'jti':jti,'sig':jwtSig}, self.private_key, algorithm=self.algorithm)
        return encoded

    def gen_encrypted_pin(self, iterString = None):
        if self.algorithm == 'EdDSA':
            return mixin_api.encrypt_ed25519_pin(self.pay_pin, self.pin_token, self.pay_session_id, self.private_key_base64, int(time.time()*1e9))

        if self.keyForAES == "":
            privKeyObj = RSA.importKey(self.private_key)
            decoded_result = base64.b64decode(self.pin_token)
            cipher = PKCS1_OAEP.new(key=privKeyObj, hashAlgo=Crypto.Hash.SHA256, label=self.pay_session_id.encode("utf-8"))
            decrypted_msg = cipher.decrypt(decoded_result)
            self.keyForAES = decrypted_msg

        tsstring = int(time.time()) # unix time
        tsstring = tsstring.to_bytes(8, 'little')

        if iterString is None:
            iterator = int(time.time() * 1e9) # unix nano
            iterator = iterator.to_bytes(8, 'little')
            toEncryptContent = self.pay_pin.encode('utf8') + tsstring + iterator
        else:
            toEncryptContent = self.pay_pin.encode('utf8') + tsstring + iterString

        toPadCount = AES.block_size - len(toEncryptContent) % AES.block_size
        toEncryptContent = toEncryptContent + int.to_bytes(toPadCount, 1, 'little') * toPadCount

        iv = Random.new().read(AES.block_size)

        cipher = AES.new(self.keyForAES, AES.MODE_CBC,iv)
        encrypted_result = cipher.encrypt(toEncryptContent)

        msg = iv + encrypted_result
        encrypted_pin = base64.b64encode(msg)

        return encrypted_pin.decode()

    def __genUrl(self, path):
        """
        generate API url
        """
        return self.api_base_url + path

    async def __genGetRequest(self, path, auth_token=""):
        """
        generate GET http request
        """
        url = self.__genUrl(path)

        if auth_token == "":
            r = await self.client.get(url)
        else:
            r = await self.client.get(url, headers={"Authorization": "Bearer " + auth_token})

        r = r.json()
        if 'error' in r:
            raise Exception(r['error'])
        # print(result_obj)
        return r['data']

    async def __genPostRequest(self, path, body, auth_token=""):
        """
        generate POST http request
        """
        # generate url
        url = self.__genUrl(path)

        # transfer obj => json string
        body_in_json = json.dumps(body)

        if auth_token == "":
            r = await self.client.post(url, json=body_in_json)
        else:
            r = await self.client.post(url, json=body_in_json, headers={"Authorization": "Bearer " + auth_token})

        result_obj = r.json()
        # print(result_obj)
        return result_obj

    async def get(self, path, body=None, auth_token=""):
        return await self.__genNetworkGetRequest(path, body, auth_token)

    async def __genNetworkGetRequest(self, path, body=None, auth_token=""):
        """
        generate Mixin Network GET http request
        """
        url = self.__genUrl(path)

        if body is not None:
            body = urlencode(body)
        else:
            body = ""

        if not auth_token:
            auth_token = self.gen_get_jwt_token(path, body, str(uuid.uuid4()))

        r = await self.client.get(url, headers={"Authorization": "Bearer " + auth_token})
        result_obj = r.json()
        return result_obj

    async def post(self, path, body, auth_token=""):
        return await self.__genNetworkPostRequest(path, body, auth_token)

    # TODO: request
    async def __genNetworkPostRequest(self, path, body, auth_token=""):
        """
        generate Mixin Network POST http request
        """
        # transfer obj => json string
        if isinstance(body, (dict, list)):
            body = json.dumps(body)
        # generate robot's auth token
        if auth_token == "":
            auth_token = self.gen_post_jwt_token(path, body, str(uuid.uuid4()))
        headers = {
            'Content-Type'  : 'application/json',
            'Authorization' : 'Bearer ' + auth_token,
            "X-Request-Id": str(uuid.uuid4()),
        }
        # generate url
        url = self.__genUrl(path)
#        print(url, body)
        r = await self.client.post(url, data=body, headers=headers)
# {'error': {'status': 202, 'code': 20118, 'description': 'Invalid PIN format.'}}

        # r = requests.post(url, data=body, headers=headers)
# {'error': {'status': 202, 'code': 401, 'description': 'Unauthorized, maybe invalid token.'}}
        r = r.json()
        if 'error' in r:
            raise Exception(r['error'])
        return r['data']

    """
    ============
    MESSENGER PRIVATE APIs
    ============
    auth token need request 'https://api.mixin.one/me' to get.
    """


    async def get_my_assets(self, auth_token=""):
        """
        Read user's all assets.
        """
        return await self.__genGetRequest('/assets', auth_token)

    async def get_ghost_keys(self, user_ids, index=0, hint=''):
        body = {
            "index": index,
            "receivers": user_ids,
            "hint": hint
        }
        return await self.post('/outputs', body)

    async def get_multisigs(self):
        return await self.__genNetworkGetRequest('/multisigs?limit=500')

    async def get_my_profile(self, auth_token=''):
        """
        Read self profile.
        """
        return await self.__genGetRequest('/me', auth_token)

    async def update_my_perference(self,receive_message_source="EVERYBODY",accept_conversation_source="EVERYBODY"):
        """
        ?
        Update my preferences.
        """

        body = {
            "receive_message_source": receive_message_source,
            "accept_conversation_source": accept_conversation_source
        }

        return await self.__genPostRequest('/me/preferences', body)

    async def update_my_profile(self, full_name, auth_token, avatar_base64=""):
        """
        ?
        Update my profile.
        """
        body = {
            "full_name": full_name,
            "avatar_base64": avatar_base64
        }

        return await self.__genPostRequest('/me', body, auth_token)

    async def get_users_info(self, user_ids, auth_token):
        """
        Get users information by IDs.
        """
        return await self.__genPostRequest('/users/fetch', user_ids, auth_token)

    async def get_user_info(self, user_id, auth_token):
        """
        Get user's information by ID.
        """
        return await self.__genGetRequest('/users/' + user_id, auth_token)

    async def search_user(self, q, auth_token=""):
        """
        Search user by Mixin ID or Phone Number.
        """
        return await self.__genGetRequest('/search/' + q, auth_token)

    async def rotate_user_qr(self, auth_token):
        """
        Rotate user’s code_id.
        """
        return await self.__genGetRequest('/me/code', auth_token)

    async def get_my_friends(self, auth_token):
        """
        Get my friends.
        """
        return await self.__genGetRequest('/friends', auth_token)

    async def create_conv(self, category, conversation_id, participants, action, role, user_id, auth_token):
        """
        Create a GROUP or CONTACT conversation.
        """
        body = {
            "category": category,
            "conversation_id": conversation_id,
            "participants": participants,
            "action": action,
            "role": role,
            "user_id": user_id
        }

        return await self.post('/conversations', body, auth_token)

    async def get_conv(self, conversation_id, auth_token=None):
        """
        Read conversation by conversation_id.
        """
        return await self.get(f'/conversations/{conversation_id}', auth_token)

    async def send_messages(self, messages):
        '''
        [
            {
                "conversation_id": "UUID",
                "recipient_id": "UUID",
                "message_id": "UUID",
                "category": "",
                "representative_id": "UUID",
                "quote_message_id": "UUID",
                "data": "Base64 encoded data"
            }
        ]
        '''
        return await self.post('/messages', messages)

    async def send_message(self, conversation_id: str, category: str, data: str):
        if isinstance(data, str):
            data = data.encode()
        msg = {
            "conversation_id": conversation_id,
            # "recipient_id": self.client_id,
            "message_id": str(uuid.uuid4()),
            "category": category,
            # "representative_id": "UUID",
            # "quote_message_id": "UUID",
            "data": base64.urlsafe_b64encode(data).decode()
        }
        return await self.post('/messages', msg)

    async def send_text_message(self, conversation_id: str, data: Union[str, bytes]):
        return await self.send_message(conversation_id, "PLAIN_TEXT", data)

    async def send_sticker_message(self, conversation_id: str, name: str, album_id: str, sticker_id: str):
        '''
        data example:
            {"name":"jiayou","album_id":"fb0eea56-c09f-4372-8ff4-9799f15b0f03","sticker_id":"0083ea85-7d28-4d0e-8132-427b6c3c9507"}
        '''
        data = {
            "name": name,
            "album_id": album_id,
            "sticker_id": sticker_id
        }
        data = json.dumps(data)
        return await self.send_message(conversation_id, "PLAIN_STICKER", data)

    async def send_contract_message(self, conversation_id: str, user_id: str):
        data = {
            "user_id": user_id
        }
        data = json.dumps(data)
        return await self.send_message(conversation_id, "PLAIN_CONTACT", data)

    async def send_button_group_message(self, conversation_id: str, label: str, color: str, action: str):
        data = {
            "label": label,
            "action": action,
            "color": color
        }
        data = json.dumps([data])
        return await self.send_message(conversation_id, "APP_BUTTON_GROUP", data)

    @staticmethod
    def _convert_object_to_dict(x):
        if isinstance(x, ButtonMessage):
            return x.__dict__()
        return x

    async def send_button_group_messages(self, conversation_id: str, buttons: List[Union[dict, ButtonMessage]]):
        assert len(buttons) > 0
        if isinstance(buttons[0], ButtonMessage):
            buttons = [self._convert_object_to_dict(x) for x in buttons]
        data = json.dumps(buttons)
        return await self.send_message(conversation_id, "APP_BUTTON_GROUP", data)

    """
    ============
    NETWORK PRIVATE APIs
    ============
    auth token need robot related param to generate.
    """

    async def update_pin(self, new_pin, old_pin, auth_token=""):
        """
        PIN is used to manage user’s addresses, assets and etc. There’s no default PIN for a Mixin Network user (except APP).
        if auth_token is empty, it create robot' pin.
        if auth_token is set, it create messenger user pin.
        """
        old_inside_pay_pin = self.pay_pin
        self.pay_pin = new_pin
        newEncrypedPin = self.gen_encrypted_pin()
        if old_pin == "":
            body = {
                "old_pin": "",
                "pin": newEncrypedPin
            }
        else:

            self.pay_pin = old_pin
            oldEncryptedPin = self.gen_encrypted_pin()
            body = {
                "old_pin": oldEncryptedPin,
                "pin": newEncrypedPin
            }
        self.pay_pin = old_inside_pay_pin
        return await self.__genNetworkPostRequest('/pin/update', body, auth_token)

    async def verify_pin(self, auth_token=""):
        """
        Verify PIN if is valid or not. For example, you can verify PIN before updating it.
        if auth_token is empty, it verify robot' pin.
        if auth_token is set, it verify messenger user pin.
        """
        enPin = self.gen_encrypted_pin()
        body = {
            "pin": enPin
        }

        return await self.__genNetworkPostRequest('/pin/verify', body, auth_token)

    async def deposit(self, asset_id):
        """
        Grant an asset's deposit address, usually it is public_key, but account_name and account_tag is used for EOS.
        """
        return await self.__genNetworkGetRequest(' /assets/' + asset_id)

    async def withdrawals(self, address_id, amount, memo, trace_id=""):
        """
        withdrawals robot asset to address_id
        Tips:Get assets out of Mixin Network, neet to create an address for withdrawal.
        """
        encrypted_pin = self.gen_encrypted_pin()

        if trace_id == "":
            trace_id = str(uuid.uuid1())

        body = {
            "address_id": address_id,
            "pin": encrypted_pin,
            "amount": amount,
            "trace_id": trace_id,
            "memo": memo

        }

        return await self.__genNetworkPostRequest('/withdrawals/', body)

    async def create_address(self, asset_id, public_key = "", label = "", account_name = "", account_tag = ""):
        """
        Create an address for withdrawal, you can only withdraw through an existent address.
        """
        body = {
            "asset_id": asset_id,
            "pin": self.gen_encrypted_pin(),
            "public_key": public_key,
            "label": label,
            "account_name": account_name,
            "account_tag": account_tag,
        }
        return await self.__genNetworkPostRequest('/addresses', body)

    async def del_address(self, address_id):
        """
        Delete an address by ID.
        """
        encrypted_pin = self.gen_encrypted_pin()

        body = {"pin": encrypted_pin}

        return await self.__genNetworkPostRequest('/addresses/' + address_id + '/delete', body)

    async def get_address(self, address_id):
        """
        Read an address by ID.
        """
        return await self.__genNetworkGetRequest('/addresses/' + address_id)

    async def transfer_to(self, to_user_id, to_asset_id, to_asset_amount, memo, trace_uuid=""):
        """
        Transfer of assets between Mixin Network users.
        """
        # generate encrypted pin
        encrypted_pin = self.gen_encrypted_pin()

        body = {'asset_id': to_asset_id, 'counter_user_id': to_user_id, 'amount': str(to_asset_amount),
                'pin': encrypted_pin, 'trace_id': trace_uuid, 'memo': memo}
        if trace_uuid == "":
            body['trace_id'] = str(uuid.uuid1())

        return await self.__genNetworkPostRequest('/transfers', body)

    async def get_transfer(self, trace_id):
        """
        Read transfer by trace ID.
        """
        return await self.__genNetworkGetRequest('/transfers/trace/' + trace_id)

    async def verify_payment(self, asset_id, opponent_id, amount, trace_id):
        """
        Verify a transfer, payment status if it is 'paid' or 'pending'.
        """
        body = {
            "asset_id": asset_id,
            "opponent_id": opponent_id,
            "amount": amount,
            "trace_id": trace_id
        }

        return await self.__genNetworkPostRequest('/payments', body)

    async def get_asset(self, asset_id):
        """
        Read asset by asset ID.
        """
        return await self.__genNetworkGetRequest('/assets/' + asset_id)

    async def ext_trans(self, asset_id, public_key, account_tag, account_name, limit, offset):
        """
        Read external transactions (pending deposits) by public_key and asset_id, use account_tag for EOS.
        """
        body = {
            "asset": asset_id,
            "public_key": public_key,
            "account_tag": account_tag,
            "account_name": account_name,
            "limit": limit,
            "offset": offset
        }

        return await self.__genNetworkGetRequest('/external/transactions', body)

    async def create_user(self, session_secret, full_name):
        """
        Create a new Mixin Network user (like a normal Mixin Messenger user). You should keep PrivateKey which is used to sign an AuthenticationToken and encrypted PIN for the user.
        """
        body = {
            "session_secret": session_secret,
            "full_name": full_name
        }

        return await self.__genNetworkPostRequest('/users', body)


    """
    ===========
    NETWORK PUBLIC APIs
    ===========
    """

    async def top_assets(self):
        """
        Read top valuable assets of Mixin Network.
        """
        return await self.__genGetRequest('/network')

    async def snapshots(self, offset, asset_id, order='DESC',limit=100):
        """
        Read public snapshots of Mixin Network.
        """
        # TODO: SET offset default(UTC TIME)
        body = {
            "limit":limit,
            "offset":offset,
            "asset":asset_id,
            "order":order
        }

        return await self.__genGetRequest('/network/snapshots', body)

    async def snapshot(self, snapshot_id):
        """
        Read public snapshots of Mixin Network by ID.
        """
        return await self.__genGetRequest('/network/snapshots/' + snapshot_id)
