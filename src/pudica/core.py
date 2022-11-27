import typing
from typing import Optional
from pudica.encryptor import Encryptor
from pudica.keyfile import Key, Keyfile
from pudica.vault import VaultDefinition, Vault
import uuid


class Pudica:
    __slots__ = ("__keyfile", "__vault")

    def __init__(
        self,
        *,
        keyname: Optional[str] = None,
        keyfile_path: Optional[str] = None,
        vault_paths: Optional[str] = None,
    ) -> None:
        self.load_keyfile(keyfile_path, keyname)
        self.load_vault(vault_paths, keyname)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        del self.__keyfile
        del self.__vault

    def load_keyfile(self, keyfile_path: Optional[str] = None, keyname: Optional[str] = None):
        if keyname is not None:
            self.__keyfile = Keyfile.with_keyname(keyname, keyfile_path)
        else:
            self.__keyfile = Keyfile(keyfile_path)

    def load_vault(self, vault_paths: Optional[str] = None, keyname: Optional[str] = None):
        if keyname is not None:
            self.__vault - Vault.with_keyname(keyname, vault_paths)
        else:
            self.__vault = Vault(vault_paths)

    def encrypt(
        self,
        cleartext: typing.Union[str, bytes],
        *,
        keyname: typing.Optional[str] = None,
        cleartext_encoding: str = "utf-8",
        save_id: Optional[str] = None,
    ):
        key = self.__keyfile._get_key(keyname)
        ciphertext = Encryptor.encrypt(key, cleartext, cleartext_encoding).decode(
            "utf-8"
        )
        id = uuid.uuid4()
        vaultpath = ""
        if save_id is not None:
            id = save_id
            vaultpath = self.__vault.paths[0]
            self.__vault.add(ciphertext, id, key.keyname)
        return VaultDefinition(id, key.keyname, ciphertext, vaultpath)

    def decrypt(
        self,
        ciphertext: typing.Union[str, bytes, VaultDefinition],
        *,
        keyname: typing.Optional[str] = None,
        cleartext_encoding: str = "utf-8",
    ):
        cipherbytes = bytes()
        if isinstance(ciphertext, bytes):
            cipherbytes = ciphertext
        elif isinstance(ciphertext, str):
            cipherbytes = ciphertext.encode("utf-8")
        elif isinstance(ciphertext, VaultDefinition):
            cipherbytes = ciphertext.ciphertext.encode("utf-8")
        if keyname == None:
            keys = self.__keyfile.get_multikeys()
            cleartext = Encryptor.decrypt_multi(keys, cipherbytes)
        else:
            key = self.__keyfile._get_key(keyname)
            cleartext = Encryptor.decrypt_bytes(key, cipherbytes)
        return cleartext.decode(cleartext_encoding)

    @staticmethod
    def generate_keyfile(path: str, overwrite: bool = False):
        Keyfile.generate(path, overwrite)
    
    @staticmethod
    def generate_vault(path: str, overwrite: bool = False):
        Vault.generate(path, overwrite)
        