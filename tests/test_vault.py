import pytest
import os

from pudica.vault import *

_testpath = f".{os.path.sep}vault"


def _unlink_testpath():
    try:
        os.unlink(_testpath)
    except FileNotFoundError:
        pass


def test_init_ok():
    _unlink_testpath()
    try:
        with open(_testpath, "w", encoding="utf-8") as f:
            f.write("test[default]:badvalue")
            _ = Vault()
    finally:
        _unlink_testpath()


def test_vault_bad_env():
    _unlink_testpath()
    try:
        if "PUDICA_VAULTS" in os.environ:
            del os.environ["PUDICA_VAULTS"]
        with pytest.raises(VaultEnvVarNotSetError):
            _ = Vault()
    finally:
        _unlink_testpath()


def test_vault_not_exists():
    _unlink_testpath()
    try:
        os.environ["PUDICA_VAULTS"] = _testpath
        with pytest.raises(VaultFileNotExistsError):
            _ = Vault()
    finally:
        _unlink_testpath()


def test_vault_one_vault_not_exists():
    _unlink_testpath()
    try:
        paths = [f"{_testpath}{i}" for i in range(4)]
        for path in paths:
            with open(path, "w", encoding="utf-8"):
                pass
        os.environ["PUDICA_VAULTS"] = ":".join(paths)
        _ = Vault()
        paths.append(f"{_testpath}5")
        os.environ["PUDICA_VAULTS"] = ":".join(paths)
        with pytest.raises(VaultFileNotExistsError):
            _ = Vault()
        for path in paths[:4]:
            os.unlink(path)
    finally:
        _unlink_testpath()
