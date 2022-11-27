import typing
from typing import Optional
from pudica.encryptor import Encryptor
from pudica.keychain import Keychain
from pudica.vault import VaultDefinition, Vault
import uuid
import os


class Pudica:
    __slots__ = ("__keychain", "__vault")

    def __init__(
        self,
        *,
        keyname: Optional[str] = None,
        keychain_path: Optional[str] = None,
        vault_paths: Optional[str] = None,
    ) -> None:
        self.load_keychain(keychain_path, keyname)
        self.load_vault(vault_paths, keyname)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        del self.__keychain
        del self.__vault

    def load_keychain(
        self, keychain_path: Optional[str] = None, keyname: Optional[str] = None
    ):
        if keyname is not None:
            self.__keychain = Keychain.with_keyname(keyname, keychain_path)
        else:
            self.__keychain = Keychain(keychain_path)

    def load_vault(
        self, vault_paths: Optional[str] = None, keyname: Optional[str] = None
    ):
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
        key = self.__keychain._get_key(keyname)
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
            keys = self.__keychain.multikeys()
            cleartext = Encryptor.decrypt_multi(keys, cipherbytes)
        else:
            key = self.__keychain._get_key(keyname)
            cleartext = Encryptor.decrypt_bytes(key, cipherbytes)
        return cleartext.decode(cleartext_encoding)

    @staticmethod
    def generate_keychain(
        path: str = f"{os.path.expanduser('~')}{os.path.sep}.pudica_keychain",
        overwrite: bool = False,
    ) -> Keychain:
        return Keychain.generate(path, overwrite)

    @staticmethod
    def generate_vault(path: str, overwrite: bool = False):
        Vault.generate(path, overwrite)
