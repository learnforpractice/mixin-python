import hashlib

def unique_conversation_id(user_id: str, recipient_id: str) -> str:
    md5 = hashlib.md5()
    if user_id < recipient_id:
        md5.update(user_id.encode())
        md5.update(recipient_id.encode())
    else:
        md5.update(recipient_id.encode())
        md5.update(user_id.encode())
    digest = bytearray(md5.digest())
    digest[6] = (digest[6] & 0x0f) | 0x30
    digest[8] = (digest[8] & 0x3f) | 0x80
    return f'{digest[0:4].hex()}-{digest[4:6].hex()}-{digest[6:8].hex()}-{digest[8:10].hex()}-{digest[10:].hex()}'
