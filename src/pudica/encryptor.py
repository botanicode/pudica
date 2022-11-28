from cryptography.fernet import Fernet, MultiFernet
import os
from typing import Union, List
from pudica.keychain import Key


class Encryptor:
    @staticmethod
    def _make_fernets(keys: List[Key]) -> MultiFernet:
        fernets: List[Fernet] = list()
        for key in keys:
            fernets.append(key.fernet)
        return MultiFernet(fernets)

    @staticmethod
    def encrypt_multi(keys: List[Key], b: bytes) -> bytes:
        return Encryptor._make_fernets(keys).encrypt(b)

    @staticmethod
    def encrypt_bytes(key: Key, b: bytes) -> bytes:
        return Encryptor.encrypt_multi([key], b)

    @staticmethod
    def encrypt_str(key: Key, s: str, encoding: str = "utf-8") -> bytes:
        return Encryptor.encrypt_bytes(key, s.encode(encoding))

    @staticmethod
    def encrypt(
        key: Key, cleartext: Union[str, bytes], encoding: str = "utf-8"
    ) -> bytes:
        if isinstance(cleartext, str):
            return Encryptor.encrypt_str(key, cleartext, encoding)
        elif isinstance(cleartext, bytes):
            return Encryptor.encrypt_bytes(key, cleartext)
        raise TypeError

    @staticmethod
    def encrypt_file(key: Key, path: str, encoding: str = "utf-8") -> bytes:
        if not os.path.exists(path):
            raise FileNotFoundError
        with open(path, "r", encoding=encoding) as f:
            return Encryptor.encrypt(key, f.read())

    @staticmethod
    def decrypt_multi(keys: List[Key], b: bytes) -> bytes:
        return Encryptor._make_fernets(keys).decrypt(b)

    @staticmethod
    def decrypt_bytes(key: Key, b: bytes) -> bytes:
        return Encryptor.decrypt_multi([key], b)

    @staticmethod
    def decrypt_str(key: Key, s: str, encoding: str = "utf-8") -> bytes:
        return Encryptor.decrypt_bytes(key, s.encode(encoding))
