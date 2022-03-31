from base64 import b64decode, b64encode
from hashlib import sha256

from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

BS = AES.block_size


def pad(raw_text: str) -> str:
    """Padding for raw_text so it's ready for encryption."""
    return raw_text + (BS - len(raw_text) % BS) * chr(BS - len(raw_text) % BS)


def unpad(padded_text: str) -> str:
    """Unpadding for padded_text so it's back to raw_text state."""
    return padded_text[:-ord(padded_text[-1:])]


def pad_key(key: str) -> str:
    """Padding for key so it's ready for encryption/decryption"""
    return key + ((BS * 2) - len(key) % BS) * chr((BS * 2) - len(key) % BS)


def encrypt(raw_text: str, key: str) -> str:
    """Encrypt string of text."""
    key_test = pad_key(key)
    raw_b64 = b64encode(pad(raw_text).encode('utf-8'))
    iv = get_random_bytes(BS)
    cipher = AES.new(key_test.encode(), AES.MODE_CFB, iv)

    return hex(int.from_bytes(
        b64encode(iv + cipher.encrypt(raw_b64)),
        byteorder="big",
    ))


def decrypt(crypto_hex: str, key: str):
    """Decrypt a crypto."""
    crypto_b64 = b64encode(bytes(int(crypto_hex, 16)))
    crypto = b64decode(crypto_b64)
    cipher = AES.new(bytes.fromhex(key), AES.MODE_CFB, crypto[:AES.block_size])

    return unpad(b64decode(cipher.decrypt(crypto[AES.block_size:])).decode('utf-8'))


def sign(message: str, priv_key: str, pub_key_n: str) -> str:
    """Sign a message with private key to verify identity."""
    hash = int.from_bytes(sha256(message.encode()).digest(), byteorder="big")
    signature = pow(hash, int(priv_key, 16), int(pub_key_n, 16))

    return hex(signature)


def verify_sign(message: str, signature: str, pub_key_n: str, pub_key_e: str) -> bool:
    """Verify a signature."""
    hash = int.from_bytes(sha256(message.encode()).digest(), byteorder="big")
    hash_from_signature = pow(int(signature, 16), int(pub_key_e, 16), int(pub_key_n, 16))

    return True if hash == hash_from_signature else False
