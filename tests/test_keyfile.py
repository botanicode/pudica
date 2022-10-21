import pytest
import os
import configparser
import datetime

from pudica.keyfile import *

_testpath = f".{os.path.sep}keyfile"

def _unlink_testpath():
    try:
        os.unlink(_testpath)
    except FileNotFoundError:
        pass    

# Test that a Keyfile can be generated
def test_generate():
    _unlink_testpath()
    try:
        Keyfile.generate(_testpath)
    finally:
        assert os.path.exists(_testpath)
        _unlink_testpath()

# Test that a Keyfile has the proper fields with correct values
def test_generate_validity():
    _unlink_testpath()
    try:
        Keyfile.generate(_testpath)
    finally:
        config = configparser.ConfigParser()
        config.read(_testpath)
        assert config.sections() == ["default"]
        assert len(config["default"]["key"]) == 44
        assert config["default"].getboolean("multikey") == True
        assert config["default"]["updated"] == datetime.datetime.today().strftime('%Y-%m-%d')
        _unlink_testpath()

# Test that a duplicate Keyfile can not be generated
def test_generate_duplicate():
    _unlink_testpath()
    try:
        Keyfile.generate(_testpath)
        with pytest.raises(KeyfileExistsError):
            Keyfile.generate(_testpath)
    finally:
        _unlink_testpath()

def test_init_ok():
    _unlink_testpath()
    try:
        Keyfile.generate(_testpath)
        keyfile = Keyfile(_testpath)
        assert len(keyfile.keys) == 1
        os.environ["PUDICA_KEYFILE"] = _testpath
        keyfile = Keyfile()
        assert len(keyfile.keys) == 1
        homepath = Keyfile._HOMEPATH
        should_delete_homepath = True
        if os.path.exists(homepath):
            should_delete_homepath = False
        else:
            os.rename(_testpath, homepath)
        keyfile = Keyfile()
        assert keyfile.path == homepath
        if should_delete_homepath is True:
            os.unlink(homepath)
    finally:
        _unlink_testpath()

def test_init_bad_path():
    _unlink_testpath()
    try:
        with pytest.raises(KeyfileNotFoundError):
            Keyfile(_testpath)
    finally:
        _unlink_testpath()

def test_init_bad_env():
    _unlink_testpath()
    try:
        with pytest.raises(KeyfileNotFoundError):
            os.environ["PUDICA_KEYFILE"] = _testpath
            Keyfile()
    finally:
        _unlink_testpath()
