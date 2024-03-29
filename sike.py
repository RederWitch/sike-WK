import os
from ctypes import *

# SIKE P751
SECRET_KEY_BYTES = 644
PUBLIC_KEY_BYTES = 564
SHARED_SECRET_BYTES = 32
CIPHERTEXT_MESSAGE_BYTES = 596

SIKE_LIB_PATH = "./lib751_x64_fast.so"


class CtypeSikeApi:
    def __init__(self):
        self.sike_api = CDLL(os.path.abspath(SIKE_LIB_PATH))

    def generate_key(self):
        pk = (c_ubyte * PUBLIC_KEY_BYTES)()
        sk = (c_ubyte * SECRET_KEY_BYTES)()
        self.sike_api.crypto_kem_keypair(byref(pk), byref(sk))

        public_key_bytes = string_at(pk, PUBLIC_KEY_BYTES)
        secret_key_bytes = string_at(sk, SECRET_KEY_BYTES)

        return public_key_bytes, secret_key_bytes

    def encapsulate(self, public_key_bytes):
        pk = (c_ubyte * PUBLIC_KEY_BYTES)()

        for i in range(PUBLIC_KEY_BYTES):
            pk[i] = public_key_bytes[i]

        ss = (c_ubyte * SHARED_SECRET_BYTES)()
        ct = (c_ubyte * CIPHERTEXT_MESSAGE_BYTES)()

        self.sike_api.crypto_kem_enc(byref(ct), byref(ss), byref(pk))

        shared_secret_bytes = string_at(ss, SHARED_SECRET_BYTES)
        ciphertext_message_bytes = string_at(ct, CIPHERTEXT_MESSAGE_BYTES)

        return shared_secret_bytes, ciphertext_message_bytes

    def decapsulate(self, secret_key_bytes, ciphertext_message_bytes):
        sk = (c_ubyte * SECRET_KEY_BYTES)()
        ct = (c_ubyte * CIPHERTEXT_MESSAGE_BYTES)()

        for i in range(SECRET_KEY_BYTES):
            sk[i] = secret_key_bytes[i]
        for i in range(CIPHERTEXT_MESSAGE_BYTES):
            ct[i] = ciphertext_message_bytes[i]

        ss = (c_ubyte * SHARED_SECRET_BYTES)()

        self.sike_api.crypto_kem_dec(byref(ss), byref(ct), byref(sk))

        shared_secret_bytes = string_at(ss, SHARED_SECRET_BYTES)

        return shared_secret_bytes
