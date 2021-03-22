# -*- coding: utf-8 -*-
"""
Mixin API for Python 3.x
This SDK base on 'https://github.com/myrual/mixin_client_demo/blob/master/mixin_api.py'
some method note '?', because can't run right result, may be it will be resolved later.

env: python 3.x
code by lee.c
update at 2018.12.2
"""

from Crypto.PublicKey import RSA
import base64
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Signature import PKCS1_v1_5
import Crypto
import time
from Crypto import Random
from Crypto.Cipher import AES
import hashlib
import datetime
import jwt
import uuid
import json
from urllib.parse import urlencode

import httpx

class MixinBotApi:
    def __init__(self, mixin_config):

        # robot's config
        self.client_id = mixin_config['client_id']
        self.client_secret = mixin_config['client_secret']
        self.pay_session_id = mixin_config['session_id']
        self.pay_pin = mixin_config['pin']
        self.pin_token = mixin_config['pin_token']
        self.private_key = mixin_config['private_key']

        self.client = httpx.AsyncClient()

        self.keyForAES = ""
        # mixin api base url
        self.api_base_url = 'https://api.mixin.one'
        #self.api_base_url = 'https://mixin-api.zeromesh.net'

    """
    BASE METHON
    """

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
        encoded = jwt.encode({'uid':self.client_id, 'sid':self.pay_session_id,'iat':iat,'exp': exp, 'jti':jti,'sig':jwtSig}, self.private_key, algorithm='RS512')

        return encoded

    def gen_get_listen_signed_token(self, uristring, bodystring, jti):
        jwtSig = self.gen_get_sig(uristring, bodystring)
        iat = datetime.datetime.utcnow()
        exp = datetime.datetime.utcnow() + datetime.timedelta(seconds=200)
        encoded = jwt.encode({'uid':self.client_id, 'sid':self.pay_session_id,'iat':iat,'exp': exp, 'jti':jti,'sig':jwtSig}, self.private_key, algorithm='RS512')
        privKeyObj = RSA.importKey(self.private_key)
        signer = PKCS1_v1_5.new(privKeyObj)
        signature = signer.sign(encoded)
        return signature


    def gen_post_jwt_token(self, uristring, bodystring, jti):
        jwtSig = self.genPOSTSig(uristring, bodystring)
        iat = datetime.datetime.utcnow()
        exp = datetime.datetime.utcnow() + datetime.timedelta(seconds=200)
        encoded = jwt.encode({'uid':self.client_id, 'sid':self.pay_session_id,'iat':iat,'exp': exp, 'jti':jti,'sig':jwtSig}, self.private_key, algorithm='RS512')
        return encoded

    def gen_encryped_pin(self, iterString = None):
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

        return encrypted_pin

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

        result_obj = r.json()
        # print(result_obj)
        return result_obj['data']

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

    async def __genNetworkGetRequest(self, path, body=None, auth_token=""):
        """
        generate Mixin Network GET http request
        """
        url = self.__genUrl(path)

        if body is not None:
            body = urlencode(body)
        else:
            body = ""

        if auth_token == "":
            token = self.gen_get_jwt_token(path, body, str(uuid.uuid4()))
            auth_token = token.decode('utf8')

        r = await self.client.get(url, headers={"Authorization": "Bearer " + auth_token})
        result_obj = r.json()
        return result_obj

    # TODO: request
    async def __genNetworkPostRequest(self, path, body, auth_token=""):
        """
        generate Mixin Network POST http request
        """
        # transfer obj => json string
        body_in_json = json.dumps(body)

        # generate robot's auth token
        if auth_token == "":
            token = self.gen_post_jwt_token(path, body_in_json, str(uuid.uuid4()))
            auth_token = token.decode('utf8')
        headers = {
            'Content-Type'  : 'application/json',
            'Authorization' : 'Bearer ' + auth_token,
        }
        # generate url
        url = self.__genUrl(path)
#        print(url, body)
        r = await self.client.post(url, json=body, headers=headers)
# {'error': {'status': 202, 'code': 20118, 'description': 'Invalid PIN format.'}}

        # r = requests.post(url, data=body, headers=headers)
# {'error': {'status': 202, 'code': 401, 'description': 'Unauthorized, maybe invalid token.'}}
        result_obj = r.json()
        # print(result_obj)
        return result_obj

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

    async def post_request(self, path, body):
        return await self.__genNetworkPostRequest(path, body)

    async def get_ghost_keys(self, user_id):
        body = {"index":0, "receivers":[user_id]}
        return await self.post_request('/outputs', body)

    async def get_multi_signs(self):
        return await self.__genNetworkGetRequest('/multisigs?limit=500')

    async def get_my_profile(self, auth_token):
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

        return await self.__genPostRequest('/conversations', body, auth_token)

    async def get_conv(self, conversation_id, auth_token):
        """
        Read conversation by conversation_id.
        """
        return await self.__genGetRequest('/conversations/' + conversation_id, auth_token)


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
        newEncrypedPin = self.gen_encryped_pin()
        if old_pin == "":
            body = {
                "old_pin": "",
                "pin": newEncrypedPin.decode()
            }
        else:

            self.pay_pin = old_pin
            oldEncryptedPin = self.gen_encryped_pin()
            body = {
                "old_pin": oldEncryptedPin.decode(),
                "pin": newEncrypedPin.decode()
            }
        self.pay_pin = old_inside_pay_pin
        return await self.__genNetworkPostRequest('/pin/update', body, auth_token)

    async def verify_pin(self, auth_token=""):
        """
        Verify PIN if is valid or not. For example, you can verify PIN before updating it.
        if auth_token is empty, it verify robot' pin.
        if auth_token is set, it verify messenger user pin.
        """
        enPin = self.gen_encryped_pin()
        body = {
            "pin": enPin.decode()
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
        encrypted_pin = self.gen_encryped_pin()

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
            "pin": self.gen_encryped_pin().decode(),
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
        encrypted_pin = self.gen_encryped_pin().decode()

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
        encrypted_pin = self.gen_encryped_pin()

        body = {'asset_id': to_asset_id, 'counter_user_id': to_user_id, 'amount': str(to_asset_amount),
                'pin': encrypted_pin.decode('utf8'), 'trace_id': trace_uuid, 'memo': memo}
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
