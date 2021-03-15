# cython: c_string_type=str, c_string_encoding=ascii

from cython.operator cimport dereference as deref, preincrement as inc
from libcpp.string cimport string
from libcpp.vector cimport vector
from libcpp.map cimport map
from libcpp cimport bool
from libc.stdlib cimport malloc


cdef extern from * :
    ctypedef long long int64_t

cdef extern from "<Python.h>":
    ctypedef long long PyLongObject

    object PyBytes_FromStringAndSize(const char* str, int size)
    int _PyLong_AsByteArray(PyLongObject* v, unsigned char* bytes, size_t n, int little_endian, int is_signed)

cdef extern from "libmixin.h":
    void Init();
    int MixinMain(char* args);
    char* CreateAddress(char* _params);
    char* GetPublicKey(char* seed);

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

def main(args):
    MixinMain(args)

def init():
    Init()

def create_address(char *params):
    return CreateAddress(params)

def get_public_key(char* seed):
    return GetPublicKey(seed)

def decode_address(char* _address):
    return DecodeAddress(_address)

def decode_signature(char* signature):
    return DecodeSignature(signature)

def decrypt_ghost(char* ghostKey):
    return DecryptGhost(ghostKey)

def decode_transaction(char* raw):
    return DecodeTransaction(raw)

def encode_transaction(char* _params, char* signs):
    return EncodeTransaction(_params, signs)

def add_signatures_to_raw_transaction(char* raw, char* signs):
    return AddSignaturesToRawTransaction(raw, signs)

def build_raw_transaction(char* params):
    return BuildRawTransaction(params)

def sign_raw_transaction(char* params):
    return SignRawTransaction(params)

def sign_transaction(char* params):
    return SignTransaction(params)

def pledge_node(char* params):
    return PledgeNode(params)

def cancel_node(char* params):
    return CancelNode(params)

def decode_pledge_node(char* params):
    return DecodePledgeNode(params)

def build_transaction_with_ghost_keys(char* assetId, char* ghostKeys, char* trxHash, char* outputAmount, char* memo, int outputIndex):
    return BuildTransactionWithGhostKeys(assetId, ghostKeys, trxHash, outputAmount, memo, outputIndex)

