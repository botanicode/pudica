from typing import Optional, List, Union
from pudica.encryptor import Encryptor
from pudica.keychain import Key, Keychain
from pudica.vault import VaultDefinition, VaultManager, Vault
import uuid
import os


class Pudica:
    __slots__ = ("_keychain", "_vault")

    def __init__(
        self,
        *,
        keyname: Optional[str] = None,
        keychain_path: Optional[str] = None,
        vault_paths: Optional[str] = None,
    ) -> None:
        self.load_keychain(keychain_path, keyname)
        self.load_vault(vault_paths, keyname)

    def __enter__(self) -> "Pudica":
        return self

    def __exit__(self, exc_type, exc_value, exc_tb) -> None:
        del self._keychain
        del self._vault

    def load_keychain(
        self, keychain_path: Optional[str] = None, keyname: Optional[str] = None
    ) -> bool:
        if keyname is not None:
            self._keychain: Keychain = Keychain.with_keyname(keyname, keychain_path)
        else:
            self._keychain: Keychain = Keychain(keychain_path)
        return True

    def load_vault(
        self, vault_paths: Optional[str] = None, keyname: Optional[str] = None
    ) -> bool:
        if keyname is not None:
            self._vault: VaultManager = VaultManager.with_keyname(keyname, vault_paths)
        else:
            self._vault: VaultManager = VaultManager(vault_paths)
        return True

    def encrypt(
        self,
        cleartext: Union[str, bytes],
        *,
        keyname: Optional[str] = None,
        cleartext_encoding: str = "utf-8",
    ):
        key: Key = self._keychain._get_key(keyname)
        ciphertext: str = Encryptor.encrypt(key, cleartext, cleartext_encoding).decode(
            "utf-8"
        )
        id: uuid.UUID = uuid.uuid4()
        return VaultDefinition(id, key.keyname, ciphertext)

    def decrypt(
        self,
        ciphertext: Union[str, bytes, VaultDefinition],
        *,
        keyname: Optional[str] = None,
    ) -> bytes:
        cipherbytes: bytes = bytes()
        if isinstance(ciphertext, bytes):
            cipherbytes = ciphertext
        elif isinstance(ciphertext, str):
            cipherbytes = ciphertext.encode("utf-8")
        elif isinstance(ciphertext, VaultDefinition):
            cipherbytes = ciphertext.ciphertext.encode("utf-8")
        else:
            raise TypeError
        if keyname == None:
            keys: List[Key] = self._keychain.multikeys()
            cleartext: bytes = Encryptor.decrypt_multi(keys, cipherbytes)
        else:
            key: Key = self._keychain._get_key(keyname)
            cleartext: bytes = Encryptor.decrypt_bytes(key, cipherbytes)
        return cleartext

    def decrypt_str(
        self,
        ciphertext: Union[str, bytes, VaultDefinition],
        *,
        keyname: Optional[str] = None,
        cleartext_encoding: str = "utf-8",
    ) -> str:
        return self.decrypt(ciphertext, keyname=keyname).decode(cleartext_encoding)

    @staticmethod
    def generate_keychain(
        path: str = f"{os.path.expanduser('~')}{os.path.sep}.pudica_keychain",
        overwrite: bool = False,
    ) -> "Pudica":
        Keychain.generate(path, overwrite)
        return Pudica(keychain_path=path)

    @staticmethod
    def generate_vault(path: str, overwrite: bool = False) -> "Pudica":
        Vault.generate(path, overwrite)
        return Pudica(vault_paths=path)
