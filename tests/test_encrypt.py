from pudica.encrypt import *
from pudica.keyfile import *
import pytest

_testpath = f".{os.path.sep}keyfile"


def _unlink_testpath():
    try:
        os.unlink(_testpath)
    except FileNotFoundError:
        pass


def test_encrypt():
    _unlink_testpath()
    try:
        Keyfile.generate(_testpath)
        encryptor = Encryptor(keyfile_path=_testpath)
        cleartext = "well hello there!"
        cipher = encryptor.encrypt_str(cleartext)
        assert cleartext != cipher.decode("utf-8")
        assert encryptor.decrypt(cipher).decode("utf-8") == cleartext
    finally:
        _unlink_testpath()


def test_encrypt_file():
    _unlink_testpath()
    try:
        Keyfile.generate(_testpath)
        encryptor = Encryptor(keyfile_path=_testpath)
        cleartext = ""
        with open(_testpath, "r", encoding="utf-8") as f:
            cleartext = f.read()
        cipher = encryptor.encrypt_file(_testpath)
        assert cleartext != cipher.decode("utf-8")
        assert encryptor.decrypt(cipher).decode("utf-8") == cleartext
    finally:
        _unlink_testpath()


def test_encrypt_file_not_found():
    _unlink_testpath()
    try:
        Keyfile.generate(_testpath)
        encryptor = Encryptor(keyfile_path=_testpath)
        with pytest.raises(FileNotFoundError):
            encryptor.encrypt_file(f"{_testpath}.txt")
    finally:
        _unlink_testpath()
