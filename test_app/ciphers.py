import base64
from enum import Enum

from Crypto.Cipher import AES, XOR
from Crypto import Random

from . import DSTU


__all__ = (
    'Ciphers',
    'Modes',

    'Deencrypter',
)


BS = 16

IV = Random.new().read(AES.block_size)  # b'\xb7\xc5(\xa7\xa8g\\\x1b_\\\x04=\x07\x87\x1a!'
MODE_PCBC = 8


def chunk_string(string, length: int = BS):
    yield from (string[0 + i:length + i] for i in range(0, len(string), length))


class ChoiceEnum(Enum):
    @classmethod
    def choices(cls):
        return [(choice.name, choice.name) for choice in cls]


class Ciphers(ChoiceEnum):
    AES = AES.AESCipher
    DSTU2014 = DSTU.DSTU2014Cipher


class Modes(ChoiceEnum):
    ECB = AES.MODE_ECB
    CBC = AES.MODE_CBC
    PCBC = MODE_PCBC
    CFB = AES.MODE_CFB
    OFB = AES.MODE_OFB


class Deencrypter:

    def __init__(self, cipher: Ciphers, mode: Modes, key: str, iv: str = IV):
        self.iv = iv
        self.mode = mode
        self.key = key
        self.cipher = cipher.value(self.key, Modes.ECB.value)

    def deencrypt(self, text, reverse=False):
        res_parts = []
        prop = self.iv
        for part in chunk_string(text):
            print(part)
            res, prop = self.block_deencrypt(part, reverse, prop)
            res_parts.append(res)
        return b''.join(res_parts)

    def block_deencrypt(self, text, reverse: bool = False, prop=None):
        if self.mode == Modes.ECB:
            res = self.cipher.decrypt(text) if reverse else self.cipher.encrypt(text)
        elif self.mode == Modes.CBC:
            if reverse:
                res = XOR.new(prop).encrypt(self.cipher.decrypt(text))
                prop = text
            else:
                text = XOR.new(prop).encrypt(text)
                res = prop = self.cipher.encrypt(text)
        elif self.mode == Modes.PCBC:
            res, prop = ..., ...
        elif self.mode == Modes.CFB:
            res, prop = ..., ...
        elif self.mode == Modes.OFB:
            res, prop = ..., ...
        else:
            raise ValueError('Incorrect mode')

        return res, prop

    def encrypt(self, raw):
        if isinstance(raw, str):
            raw = bytes(raw, 'utf-8')
        print(raw)
        pad = BS - len(raw) % BS
        print(raw + pad * pad.to_bytes(1, 'big'))
        return self.deencrypt(raw + pad * pad.to_bytes(1, 'big'))

    def decrypt(self, enc):
        if isinstance(enc, str):
            enc = bytes(enc, 'utf-8')
        raw = self.deencrypt(enc, reverse=True)
        print(raw)
        return raw[:-ord(raw[len(raw) - 1:])]
