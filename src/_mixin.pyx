# cython: c_string_type=str, c_string_encoding=utf8

from cython.operator cimport dereference as deref, preincrement as inc
from cpython.bytes cimport PyBytes_AS_STRING
from libcpp.string cimport string
from libcpp.vector cimport vector
from libcpp.map cimport map
from libcpp cimport bool
from libc.stdlib cimport malloc, free


cdef extern from * :
    ctypedef long long int64_t

cdef extern from "<Python.h>":
    ctypedef long long PyLongObject

    object PyBytes_FromStringAndSize(const char* str, int size)
    int _PyLong_AsByteArray(PyLongObject* v, unsigned char* bytes, size_t n, int little_endian, int is_signed)

cdef extern from "libmixin.h" nogil:
    void Init();
    char* GetMixinVersion()
    int MixinMain(char* args)
    char* CreateAddress(char* _params);
    char* GetPublicKey(char* seed);
    char* GenerateRandomSeed();

    char* DecodeAddress(char* _address);
    char* DecodeSignature(char* _signature);
    char* DecryptGhost(char* _ghostKey);
    char* DecodeTransaction(char* _raw);
    char* EncodeTransaction(char* _params, char* _signs);
    char* BuildRawTransaction(char* _params);
    char* SignTransaction(char* _params);
    char* PledgeNode(char* _params);
    char* CancelNode(char* _params);
    char* DecodePledgeNode(char* _params);

    char* AddSignaturesToRawTransaction(char* raw, char* signs);

    char* BuildTransactionWithGhostKeys(char* assetId, char* ghostKeys, char* trxHash, char* outputAmount, char* memo, int outputIndex)

    char* SignRawTransaction(char* params)

    char* SignMessage(char* _key, char* _msg);
    char* VerifySignature(char* _msg, char* _pub, char* _sig);
    char* GetAssetId(char* asset);
    char* GetFeeAssetId(char* asset);
    bool BatchVerify(char* msg, int msg_size, char** keys, int keys_size, char** sigs, int sigs_size);
    char* NewGhostKeys(char* seed, char* accounts, int outputs);


cdef object convert(char *_ret):
    ret = <object>_ret
    free(_ret)
    return ret

def main(_args):
    cdef char* args
    args = _args
    with nogil:
        MixinMain(args)

def init():
    Init()

def get_mixin_version():
    cdef char* ret
    ret = GetMixinVersion()
    return convert(ret)

def create_address(char *params):
    cdef char *_ret
    _ret =  CreateAddress(params)
    return convert(_ret)

def get_public_key(char* seed):
    cdef char *_ret
    _ret = GetPublicKey(seed)
    return convert(_ret)

def generate_random_seed():
    cdef char* ret
    ret = GenerateRandomSeed()
    return convert(ret)

def decode_address(char* _address):
    cdef char *_ret
    _ret = DecodeAddress(_address)
    return convert(_ret)

def decode_signature(char* signature):
    cdef char *_ret
    _ret = DecodeSignature(signature)
    return convert(_ret)

def decrypt_ghost(char* ghostKey):
    cdef char *_ret
    _ret = DecryptGhost(ghostKey)
    return convert(_ret)

def decode_transaction(char* raw):
    cdef char *_ret
    _ret = DecodeTransaction(raw)
    return convert(_ret)

def encode_transaction(char* _params, char* signs):
    cdef char *_ret
    _ret = EncodeTransaction(_params, signs)
    return convert(_ret)

def add_signatures_to_raw_transaction(char* raw, char* signs):
    cdef char *_ret
    _ret = AddSignaturesToRawTransaction(raw, signs)
    return convert(_ret)

def build_raw_transaction(char* params):
    cdef char *_ret
    _ret = BuildRawTransaction(params)
    return convert(_ret)

def sign_raw_transaction(char* params):
    cdef char *_ret
    _ret = SignRawTransaction(params)
    return convert(_ret)

def sign_transaction(char* params):
    cdef char *_ret
    _ret = SignTransaction(params)
    return convert(_ret)

def pledge_node(char* params):
    cdef char *_ret
    _ret = PledgeNode(params)
    return convert(_ret)

def cancel_node(char* params):
    cdef char *_ret
    _ret = CancelNode(params)
    return convert(_ret)

def decode_pledge_node(char* params):
    cdef char *_ret
    _ret = DecodePledgeNode(params)
    return convert(_ret)

def build_transaction_with_ghost_keys(char* assetId, char* ghostKeys, char* trxHash, char* outputAmount, char* memo, int outputIndex):
    cdef char *_ret
    _ret = BuildTransactionWithGhostKeys(assetId, ghostKeys, trxHash, outputAmount, memo, outputIndex)
    return convert(_ret)

def sign_message(char* _key, char* _msg):
    cdef char *_ret
    _ret = SignMessage(_key, _msg)
    return convert(_ret)

def verify_signature(char* _msg, char* _pub, char* _sig):
    cdef char *_ret
    _ret = VerifySignature(_msg, _pub, _sig)
    return convert(_ret)

def get_asset_id(char *asset):
    cdef char *ret
    ret = GetAssetId(asset)
    return convert(ret)

def get_fee_asset_id(char *asset):
    cdef char *ret
    ret = GetFeeAssetId(asset)
    return convert(ret)

def batch_verify(msg, keys, sigs):
    cdef char **_keys
    cdef char **_sigs
    if not len(keys) == len(sigs):
        raise Exception('keys and signature size not the same')
    for i in range(len(keys)):
        if not len(keys[i]) == 32:
            raise Exception('bad key size')
        if not len(sigs[i]) == 64:
            raise Exception('bad signature size')
    _keys = <char **>malloc(sizeof(char **) * len(keys))
    _sigs = <char **>malloc(sizeof(char **) * len(sigs))
    for i in range(len(keys)):
        _keys[i] = PyBytes_AS_STRING(keys[i])
        _sigs[i] = PyBytes_AS_STRING(sigs[i])
    ret = BatchVerify(msg, len(msg), _keys, len(keys), _sigs, len(sigs))
    free(<void *>_keys)
    free(<void *>_sigs)
    return ret

def new_ghost_keys(char *seed, char* accounts, int outputs):
    return NewGhostKeys(seed, accounts, outputs)

