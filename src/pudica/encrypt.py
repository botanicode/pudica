from cryptography.fernet import Fernet, MultiFernet
from pudica.keyfile import *


class Encryptor:
    __slots__ = "fernets"

    def __init__(
        self,
        *,
        keyfile_path: typing.Optional[str] = None,
        keyfile_label: typing.Optional[str] = "default"
    ):
        keyfile = Keyfile(path=keyfile_path, label=keyfile_label)
        keys = [Fernet(x["key"].encode("utf-8")) for x in keyfile.keys]
        self.fernets = MultiFernet(keys)

    def encrypt(self, b: bytes) -> bytes:
        return self.fernets.encrypt(b)

    def encrypt_str(self, s: str) -> bytes:
        return self.encrypt(s.encode("utf-8"))

    def encrypt_file(self, path: str, encoding: str = "utf-8") -> bytes:
        if not os.path.exists(path):
            raise FileNotFoundError
        with open(path, "r", encoding=encoding) as f:
            return self.encrypt_str(f.read())

    def decrypt(self, b: bytes) -> bytes:
        return self.fernets.decrypt(b)
