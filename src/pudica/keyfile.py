import os
import typing
from cryptography.fernet import Fernet
import configparser
import datetime

class KeyfileNotFoundError(FileNotFoundError):
    pass

class KeyfileExistsError(FileNotFoundError):
    pass

class KeyfileLabelNotExistsError(ValueError):
    pass

class Keyfile:
    __slots__ = ("path", "keys")
    _HOMEPATH=f"{os.path.expanduser('~')}{os.path.sep}.pudica_keyfile"

    def __configtodict(self, configitem) -> typing.Dict[str, typing.Any]:
        strings = ("key", "updated")
        bools = ("multikey")
        keyobj = dict()
        for key in configitem:
            if key in strings:
                keyobj[key] = configitem[key]
            elif key in bools:
                keyobj[key] = configitem.getboolean(key)
        return keyobj


    def __init__(self, path: typing.Optional[str] = None, label: typing.Optional[str] = None):
        if path is not None:
            if os.path.exists(path):
                self.path = path
            else:
                raise KeyfileNotFoundError("")
        elif "PUDICA_KEYFILE" in os.environ and os.path.exists((envpath := os.environ["PUDICA_KEYFILE"])):
            self.path = envpath
        else:
            if os.path.exists(self._HOMEPATH):
                self.path = self._HOMEPATH
            else:
                raise KeyfileNotFoundError
        config = configparser.ConfigParser()
        config.read(self.path)
        self.keys: typing.List = list()
        if label is not None:
            if label not in config.sections():
                raise KeyfileLabelNotExistsError
            self.keys.append(config[label])
        else:
            for configlabel in config.sections():
                if config[configlabel].getboolean("multikey") is True:
                    self.keys.append(self.__configtodict(config[configlabel]))

        

    @staticmethod
    def generate(path: str, label: str = "default", ) -> "Keyfile":
        if os.path.exists(path):
            raise KeyfileExistsError
        newkeyfile = configparser.ConfigParser()
        newkeyfile[label] = {
            "key": Fernet.generate_key().decode("utf-8"),
            "multikey": True,
            "updated": datetime.datetime.today().strftime('%Y-%m-%d')
        }
        with open(path, "w", encoding="utf-8") as f:
            newkeyfile.write(f)
        return Keyfile(path=path)