from enum import Enum

from Crypto.Cipher import AES, XOR
from Crypto import Random

from . import DSTU


__all__ = (
    'Ciphers',
    'Modes',

    'Deencrypter',
)


def default_key():
    return b'\x11\x94\xfb\xbc\xf1\xa3>pd\xf5\xa5\xcdd\xccSS'


# IV = Random.new().read(AES.block_size)
IV = b'\xb7\xc5(\xa7\xa8g\\\x1b_\\\x04=\x07\x87\x1a!'
MODE_PCBC = 8


def chunk_string(string, length: int = AES.block_size):
    yield from (string[0 + i:length + i] for i in range(0, len(string), length))


class ChoiceEnum(Enum):
    @classmethod
    def choices(cls):
        return [(choice.name, choice.value) for choice in cls]


class Ciphers(ChoiceEnum):
    AES = 'AES'
    Kalina = 'Kalina'


ciphers = {
    Ciphers.AES: AES.AESCipher,
    Ciphers.Kalina: DSTU.DSTU2014Cipher,
}


class Modes(ChoiceEnum):
    ECB = 'ECB'
    CBC = 'CBC'
    PCBC = 'PCBC'
    CFB = 'CFB'
    OFB = 'OFB'


class Deencrypter:

    def __init__(self, cipher: Ciphers, mode: Modes, key: str, iv: str = IV):
        self.iv = iv
        self.mode = mode
        self.key = key
        self.cipher = ciphers[cipher](self.key, AES.MODE_ECB)

    def deencrypt(self, text, reverse=False):
        res_parts = []
        prop = self.iv
        for part in chunk_string(text):
            res, prop = self.block_deencrypt(part, reverse, prop)
            res_parts.append(res)
        return b''.join(res_parts)

    def block_deencrypt(self, text, reverse, prop=None):
        if self.mode == Modes.ECB:
            res = self.cipher.decrypt(text) if reverse else self.cipher.encrypt(text)
        elif self.mode == Modes.CBC:
            if reverse:
                res, prop = XOR.new(prop).encrypt(self.cipher.decrypt(text)), text
            else:
                res = prop = self.cipher.encrypt(XOR.new(prop).encrypt(text))
        elif self.mode == Modes.PCBC:
            if reverse:
                res = XOR.new(prop).encrypt(self.cipher.decrypt(text))
            else:
                res = self.cipher.encrypt(XOR.new(prop).encrypt(text))
            prop = XOR.new(res).encrypt(text)
        elif self.mode == Modes.CFB:
            if reverse:
                res, prop = XOR.new(text).encrypt(self.cipher.encrypt(prop)), text
            else:
                res = prop = XOR.new(text).encrypt(self.cipher.encrypt(prop))
        elif self.mode == Modes.OFB:
            prop = self.cipher.encrypt(prop)
            res = XOR.new(prop).encrypt(text)
        else:
            raise ValueError('Incorrect mode')

        return res, prop

    def encrypt(self, raw):
        if isinstance(raw, str):
            raw = bytes(raw, 'utf-8')
        pad = AES.block_size - len(raw) % AES.block_size
        return self.deencrypt(raw + pad * pad.to_bytes(1, 'big'))

    def decrypt(self, enc):
        if isinstance(enc, str):
            enc = bytes(enc, 'utf-8')
        raw = self.deencrypt(enc, reverse=True)
        return raw[:-ord(raw[len(raw) - 1:])]
