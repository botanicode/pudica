import datetime
import os
import json
from typing import Optional, List, Dict, Any
import logging
from dataclasses import dataclass
from cryptography.fernet import Fernet
from pudica.errors import (
    KeychainKeynameNotExistsError,
    KeychainNotFoundError,
    KeychainWriteFailureError,
    KeyMalformedError,
    KeychainExistsError,
)
import shutil
import base64


@dataclass
class Key:
    keyname: str
    fernet: Optional[Fernet]
    multikey: bool
    updated: Optional[str]

    def __str__(self) -> str:
        return f"Key({self.keyname}: updated {self.updated})"

    def __repr__(self) -> str:
        return self.__str__()

    @staticmethod
    def fromdict(d: Dict[str, Any]) -> "Key":
        if "keyname" not in d:
            logging.error(f"Key failed to load - missing keyname")
            raise KeyMalformedError
        fernet: Optional[Fernet] = None
        if "fernet" in d:
            fernet = Fernet(d["fernet"].encode("utf-8"))
        return Key(
            keyname=d["keyname"],
            fernet=fernet,
            multikey=d.get("multikey", False),
            updated=d.get("updated", None),
        )

    def todict(self) -> Dict[str, Any]:
        return {
            "keyname": self.keyname,
            "fernet": base64.b64encode(
                self.fernet._signing_key + self.fernet._encryption_key
            ).decode("utf-8"),
            "multikey": self.multikey,
            "updated": self.updated,
        }

    @staticmethod
    def new(keyname: str, multikey: bool = True) -> "Key":
        keydict = {
            "keyname": keyname,
            "fernet": Fernet.generate_key().decode("utf-8"),
            "multikey": multikey,
            "updated": datetime.datetime.today().strftime("%Y-%m-%d"),
        }
        return Key.fromdict(keydict)


class Keychain:
    __slots__ = ("path", "keys")

    def __init__(self, path: Optional[str] = None) -> None:
        logging.debug("Reading keychain...")
        working_path: Optional[str] = path
        if working_path is None:
            logging.debug(
                'Keychain path not provided in Keychain.__init__(), checking "PUDICA_KEYCHAIN" environment variable...'
            )
            if "PUDICA_KEYCHAIN" not in os.environ:
                logging.error(
                    'Keychain path not provided in Keychain.__init__(), "PUDICA_KEYCHAIN" environment variable not present.'
                )
                raise KeychainNotFoundError
            working_path = os.environ["PUDICA_KEYCHAIN"]
            logging.debug(
                f'Reading keychain from "PUDICA_KEYCHAIN" environment variable: `{working_path}`'
            )
        else:
            logging.debug(f"Reading keychain from provided path: `{working_path}`...")
        self.path: str = working_path
        with open(working_path, "r", encoding="utf-8") as f:
            keychain: Dict[str, Any] = json.load(f)
            self.keys: List[Key] = list()
            for key in keychain["keys"]:
                self.keys.append(Key.fromdict(key))
        logging.debug(f"Loaded {len(self.keys)} keys")
        return

    def _todict(self) -> Dict[str, Any]:
        return {"keys": [key.todict() for key in self.keys]}

    def _save(self, delete_backup: bool = True) -> bool:
        logging.debug(f"Saving keychain...")
        logging.debug(f"Backing up keychain...")
        backup_path: str = f"{self.path}_backup"
        shutil.copyfile(self.path, backup_path)
        errored: bool = False
        try:
            logging.debug(f"Writing updated keychain...")
            with open(self.path, "w", encoding="utf-8") as f:
                f.write(json.dumps(self._todict(), indent="\t"))
            logging.debug(f"Updated keychain written")
        except Exception as e:
            logging.error(f"Writing updated keychain failed: {e}")
            logging.error(f"Restoring original keychain")
            shutil.copyfile(backup_path, self.path)
            errored = True
        if delete_backup:
            os.unlink(backup_path)
            logging.debug(f"Backup keychain deleted")
        if errored:
            raise KeychainWriteFailureError
        logging.debug(f"Keychain update complete")
        return True

    def _get_key(self, keyname: Optional[str]) -> Key:
        if keyname is None:
            logging.debug(f"Keyname not provided, returning default key...")
            return self.default_key()
        logging.debug(f"Finding key `{keyname}`...")
        keys: List[Key] = [key for key in self.keys if key.keyname == keyname]
        if len(keys) < 1:
            logging.error(f"Keyname `{keyname}` does not exist in keychain")
            raise KeychainKeynameNotExistsError
        logging.debug(f"Key `{keyname}` found")
        return keys[0]

    def _get_multikeys(self) -> List[Key]:
        logging.debug(f"Getting multikeys...")
        keys: List[Key] = [key for key in self.keys if key.multikey]
        logging.debug(f"Found {len(keys)} multikeys")
        return keys

    def add_key(self, key: Key, replace_existing: bool = True) -> bool:
        logging.debug(f"Adding key `{key.keyname}`...")
        added: bool = False
        if replace_existing:
            for i, currkey in enumerate(self.keys):
                if currkey.keyname == key.keyname:
                    self.keys[i] = key
                    added = True
                    logging.debug(f"Key `{key.keyname}` exists, overwritten")
                    break
        if not added:
            self.keys.append(key)
        logging.debug(f"Key `{key.keyname}` added")
        self._save()
        return True

    def new_key(
        self,
        keyname: str,
        multikey: bool = True,
        save_to_keychain: bool = True,
        replace_existing: bool = True,
    ) -> Key:
        logging.debug(f"Creating new key `{keyname}`...")
        key: Key = Key.new(keyname, multikey)
        if save_to_keychain:
            self.add_key(key, replace_existing)
        logging.debug(f"Key `{keyname}` created")
        return key

    def default_key(self) -> Key:
        logging.debug(f"Getting default key...")
        default_keyname: str = "default"
        for key in self.keys:
            if key.keyname == default_keyname:
                logging.debug(f"Key `{default_keyname}` exists")
                return key
        logging.debug(f"Key `{default_keyname}` does not exist, returning first key")
        return self.keys[0]

    @staticmethod
    def key(keyname: str = "default", path: Optional[str] = None) -> Key:
        keychain: Keychain = Keychain(path=path)
        return keychain._get_key(keyname)

    @staticmethod
    def with_keyname(
        keyname: str = "default", path: Optional[str] = None
    ) -> "Keychain":
        keychain: Keychain = Keychain(path=path)
        keychain.keys = [keychain._get_key(keyname)]
        return keychain

    @staticmethod
    def multikeys(path: Optional[str] = None) -> List[Key]:
        keychain: Keychain = Keychain(path=path)
        return keychain._get_multikeys()

    @staticmethod
    def generate(path: str, overwrite: bool = False) -> "Keychain":
        logging.debug(f"Generating new keychain at path `{path}`...")
        if os.path.exists(path) and overwrite is False:
            logging.error(f"Keychain already exists at `{path}`")
            raise KeychainExistsError
        newkeychain = {"keys": list()}
        with open(path, "w", encoding="utf-8") as f:
            f.write(json.dumps(newkeychain, indent="\t"))
        logging.debug(f"New keychain generated at `{path}`")
        keychain: Keychain = Keychain(path)
        keychain.new_key("default")
        return keychain
