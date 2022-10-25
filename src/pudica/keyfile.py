import os
import typing
from cryptography.fernet import Fernet
import configparser
import datetime
from pudica.errors import *


class Keyfile:
    __slots__ = ("path", "keys")
    _HOMEPATH: str = f"{os.path.expanduser('~')}{os.path.sep}.pudica_keyfile"

    def __configtodict(self, configitem) -> typing.Dict[str, typing.Union[str, bool]]:
        strings: typing.Tuple[str] = ("key", "updated")
        bools: typing.Tuple[str] = "multikey"
        keyobj: typing.Dict[str, typing.Union[str, bool]] = dict()
        for key in configitem:
            if key in strings:
                keyobj[key] = configitem[key]
            elif key in bools:
                keyobj[key] = configitem.getboolean(key)
        return keyobj

    def _readkeyfile(self):
        config = configparser.ConfigParser()
        config.read(self.path)
        return config

    def _parsekeys(self, label: typing.Optional[str] = None):
        config = self._readkeyfile()
        self.keys: typing.List[typing.Dict[str, typing.Union[str, bool]]] = list()
        if label is not None:
            if label not in config.sections():
                raise KeyfileLabelNotExistsError
            self.keys.append(self.__configtodict(config[label]))
        else:
            for configlabel in config.sections():
                if config[configlabel].getboolean("multikey") is True:
                    self.keys.append(self.__configtodict(config[configlabel]))

    @staticmethod
    def _newkey() -> typing.Dict:
        return {
            "key": Fernet.generate_key().decode("utf-8"),
            "multikey": True,
            "updated": datetime.datetime.today().strftime("%Y-%m-%d"),
        }

    def __init__(
        self, path: typing.Optional[str] = None, label: typing.Optional[str] = None
    ):
        if path is not None:
            if os.path.exists(path):
                self.path = path
            else:
                raise KeyfileNotFoundError("")
        elif "PUDICA_KEYFILE" in os.environ and os.path.exists(
            (envpath := os.environ["PUDICA_KEYFILE"])
        ):
            self.path = envpath
        else:
            if os.path.exists(self._HOMEPATH):
                self.path = self._HOMEPATH
            else:
                raise KeyfileNotFoundError
        self._parsekeys(label=label)

    def add_key(self, label: str):
        config = self._readkeyfile()
        if label in config.sections():
            raise KeyfileLabelExistsError
        config[label] = Keyfile._newkey()
        with open(self.path, "w", encoding="utf-8") as f:
            config.write(f)
        self._parsekeys(label)

    def delete_key(self, label: str):
        config = self._readkeyfile()
        if label not in config.sections():
            raise KeyfileLabelNotExistsError
        config.remove_section(label)
        with open(self.path, "w", encoding="utf-8") as f:
            config.write(f)
        self._parsekeys()

    def update_key(self, label: str):
        self.delete_key(label)
        self.add_key(label)

    @staticmethod
    def generate(
        path: str,
        label: str = "default",
    ) -> "Keyfile":
        if os.path.exists(path):
            raise KeyfileExistsError
        newkeyfile = configparser.ConfigParser()
        newkeyfile[label] = Keyfile._newkey()
        with open(path, "w", encoding="utf-8") as f:
            newkeyfile.write(f)
        return Keyfile(path=path)
