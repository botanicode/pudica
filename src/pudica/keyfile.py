import datetime
import os
import json
from typing import Optional, List
import logging
from dataclasses import dataclass
from cryptography.fernet import Fernet
from pudica.errors import (
    KeyfileKeynameNotExistsError,
    KeyfileNotFoundError,
    KeyfileWriteFailureError,
)
import shutil


@dataclass
class Key:
    keyname: str
    fernet: str
    multikey: bool
    updated: str

    def __str__(self):
        return f"Key({self.keyname}: updated {self.updated})"

    def __repr__(self):
        return self.__str__()

    @staticmethod
    def fromdict(d):
        if (
            "keyname" not in d
            or "fernet" not in d
            or "multikey" not in d
            or "updated" not in d
        ):
            raise ValueError
        return Key(
            keyname=d["keyname"],
            fernet=d["fernet"],
            multikey=d["multikey"],
            updated=d["updated"],
        )

    def todict(self):
        return {
            "keyname": self.keyname,
            "fernet": self.fernet,
            "multikey": self.multikey,
            "updated": self.updated,
        }

    @staticmethod
    def new(keyname, multikey=True):
        keydict = {
            "keyname": keyname,
            "fernet": Fernet.generate_key().decode("utf-8"),
            "multikey": multikey,
            "updated": datetime.datetime.today().strftime("%Y-%m-%d"),
        }
        return Key.fromdict(keydict)


class Keyfile:
    __slots__ = ("path", "keys")

    def __init__(self, path: Optional[str] = None) -> None:
        logging.debug("Reading keyfile...")
        working_path = path
        if working_path is None:
            logging.debug(
                'Keyfile path not provided in Keyfile.__init__(), checking "PUDICA_KEYFILE" environment variable...'
            )
            if "PUDICA_KEYFILE" not in os.environ:
                logging.error(
                    'Keyfile path not provided in Keyfile.__init__(), "PUDICA_KEYFILE" environment variable not present.'
                )
                raise KeyfileNotFoundError
            working_path = os.environ["PUDICA_KEYFILE"]
            logging.debug(
                f'Reading keyfile from "PUDICA_KEYFILE" environment variable: `{working_path}`'
            )
        else:
            logging.debug(f"Reading keyfile from provided path: `{working_path}`")
        self.path = working_path
        with open(working_path, "r", encoding="utf-8") as f:
            keyfile = json.load(f)
            self.keys: List[Key] = list()
            for key in keyfile["keys"]:
                self.keys.append(Key.fromdict(key))
        return

    def _to_dict(self):
        return {"keys": [key.todict() for key in self.keys]}

    def _save(self, delete_backup: bool = True):
        logging.debug(f"Saving keyfile...")
        logging.debug(f"Backing up keyfile...")
        backup_path = f"{self.path}_backup"
        shutil.copyfile(self.path, backup_path)
        errored = False
        try:
            logging.debug(f"Writing updated keyfile...")
            with open(self.path, "w", encoding="utf-8") as f:
                f.write(json.dumps(self._to_dict(), indent="\t"))
            logging.debug(f"Updated keyfile written")
        except:
            logging.error(f"Writing updated keyfile failed")
            logging.debug(f"Restoring original keyfile")
            shutil.copyfile(backup_path, self.path)
            errored = True
        if delete_backup:
            os.unlink(backup_path)
        if errored:
            raise KeyfileWriteFailureError

    def _get_key(self, keyname: Optional[str]):
        logging.debug(f"Finding key `{keyname}`...")
        if keyname is None:
            return self.default_key()
        key = [key for key in self.keys if key.keyname == keyname]
        if len(key) < 1:
            logging.error(f"Keyname `{keyname}` does not exist in keyfile")
            raise KeyfileKeynameNotExistsError
        logging.debug(f"Key `{keyname}` found")
        return key[0]

    def _get_multikeys(self):
        logging.debug(f"Getting multikeys...")
        keys = [key for key in self.keys if key.multikey]
        logging.debug(f"Found {len(keys)} multikeys")
        return keys

    def add_key(self, key, replace_existing: bool = True):
        added = False
        if replace_existing:
            for i, currkey in enumerate(self.keys):
                if currkey.keyname == key.keyname:
                    self.keys[i] = key
                    added = True
                    break
        if not added:
            self.keys.append(key)
        self._save()

    def new_key(
        self,
        keyname,
        multikey: bool = True,
        save_to_keyfile: bool = True,
        replace_existing: bool = True,
    ):
        logging.debug(f"Creating new key named `{keyname}`...")
        key: Key = Key.new(keyname, multikey)
        if save_to_keyfile:
            self.add_key(key, replace_existing)
        logging.debug(f"Key named `{keyname}` created")
        return key

    def default_key(self):
        for key in self.keys:
            if key.keyname == "default":
                return key
        return self.keys[0]

    @staticmethod
    def get_key(keyname: str = "default", path: Optional[str] = None):
        keyfile = Keyfile(path=path)
        return keyfile._get_key(keyname)

    @staticmethod
    def with_keyname(keyname: str = "default", path: Optional[str] = None):
        keyfile = Keyfile(path=path)
        keyfile.keys = [keyfile._get_key(keyname)]
        return keyfile

    @staticmethod
    def get_multikeys(path: Optional[str] = None):
        keyfile = Keyfile(path=path)
        return keyfile._get_multikeys()

    @staticmethod
    def generate(path: str, overwrite: bool = False):
        if os.path.exists(path) and overwrite is False:
            raise FileExistsError
        newvault = {"keys": list()}
        with open(path, "w", encoding="utf-8") as f:
            f.write(json.dumps(newvault, indent="\t"))
