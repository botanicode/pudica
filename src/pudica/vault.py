import logging
from typing import Optional, List
import os
from pudica.errors import VaultEnvVarNotSetError, VaultDefinitionNotExistsError
import json
from dataclasses import dataclass


@dataclass
class VaultDefinition:
    id: str
    keyname: Optional[str]
    ciphertext: str
    vaultpath: str

    def __str__(self):
        return f"VaultDefinition({self.id}: encrypted using {self.keyname})"

    def __repr__(self):
        return self.__str__()

    @staticmethod
    def fromdict(d, vaultpath):
        if "id" not in d or "keyname" not in d or "ciphertext" not in d:
            raise ValueError
        return VaultDefinition(
            id=d["id"],
            keyname=d["keyname"],
            ciphertext=d["ciphertext"],
            vaultpath=vaultpath,
        )

    def todict(self):
        return {"id": self.id, "keyname": self.keyname, "ciphertext": self.ciphertext}

    @staticmethod
    def new(id, keyname, ciphertext, vaultpath):
        return VaultDefinition(
            id=id, keyname=keyname, ciphertext=ciphertext, vaultpath=vaultpath
        )


class Vault:
    __slots__ = ("paths", "definitions")

    def __init__(self, paths: Optional[str] = None) -> None:
        logging.debug("Reading vault(s)...")
        working_paths = paths
        if working_paths is None:
            logging.debug(
                'Vault paths not provided in Vault.__init__(), checking "PUDICA_VAULTS" environment variable...'
            )
            if "PUDICA_VAULTS" not in os.environ:
                logging.debug(
                    'Vault paths not provided in Vault.__init__(), "PUDICA_VAULTS" environment variable not present'
                )
                raise VaultEnvVarNotSetError
            working_paths = os.environ["PUDICA_VAULTS"]
            logging.debug(
                f'Reading vault(s) from "PUDICA_VAULTS" environment variable: `{working_paths}`'
            )
        else:
            logging.debug(f"Reading vault(s) from provided paths: `{working_paths}`")
        self.paths: List[str] = working_paths.split(":")
        self.definitions: List[VaultDefinition] = list()
        for path in self.paths:
            with open(path, "r", encoding="utf-8") as f:
                vault_data = json.loads(f.read())
                for definition in vault_data["definitions"]:
                    self.definitions.append(VaultDefinition.fromdict(definition, path))
        logging.debug(
            f"Loaded {len(self.definitions)} definition(s) from {len(self.paths)} vault(s)"
        )

    def get(self, id: Optional[str] = None, keyname: Optional[str] = None):
        logging.debug(
            f"Finding vault definition with id `{'*' if id is None else id}` and keyname `{'null' if keyname is None else keyname}`..."
        )
        definitions: List[VaultDefinition] = self.definitions
        definitions = [
            definition for definition in definitions if definition.keyname == keyname
        ]
        if id is not None:
            definitions = [
                definition for definition in definitions if definition.id == id
            ]
        if len(definitions) < 1:
            raise VaultDefinitionNotExistsError
        logging.debug(f"Found {len(definitions)} matching definition(s)")
        if id is not None:
            return definitions[0]
        return definitions

    def add(
        self,
        ciphertext,
        id,
        keyname: Optional[str] = None,
        vaultpath: Optional[str] = None,
        replace_extisting: bool = True,
    ):
        logging.debug(f"Adding definition with id `{id}` to vault...")
        working_vaultpath = vaultpath
        if working_vaultpath is None:
            working_vaultpath = self.paths[0]
            logging.debug(
                f"Vault path not prodived, adding definition to vault at path`{working_vaultpath}`..."
            )
        else:
            logging.debug(
                f"Adding definition to provided vault at path`{working_vaultpath}`..."
            )
        working_keyname = keyname
        if working_keyname is None:
            logging.debug(
                f"Keyname not prodived, adding definition to vault without keyname..."
            )
        else:
            logging.debug(
                f"Adding definition to vault with keyname `{working_keyname}`..."
            )
        with open(working_vaultpath, "r", encoding="utf-8") as f:
            vaultdata = json.loads(f.read())
        found_at = -1
        if replace_extisting:
            for i, definition in enumerate(vaultdata["definitions"]):
                if definition["id"] == id and definition["keyname"] == keyname:
                    found_at = i
                    break
        newdefinition = VaultDefinition(
            id=id, keyname=keyname, ciphertext=ciphertext, vaultpath=working_vaultpath
        ).todict()
        if found_at < 0:
            vaultdata["definitions"].append(newdefinition)
        else:
            vaultdata["definitions"][found_at] = newdefinition
        with open(working_vaultpath, "w", encoding="utf-8") as f:
            f.write(json.dumps(vaultdata, indent="\t"))

    @staticmethod
    def with_keyname(keyname, paths: Optional[str] = None) -> "Vault":
        vault = Vault(paths=paths)
        vault.definitions = vault.get(keyname=keyname)
        return vault

    @staticmethod
    def get_definition(id, keyname: Optional[str] = None) -> VaultDefinition:
        vault = Vault()
        return vault.get(id, keyname)

    @staticmethod
    def generate(path: str, overwrite: bool = False):
        if os.path.exists(path) and overwrite is False:
            raise FileExistsError
        newvault = {"definitions": list()}
        with open(path, "w", encoding="utf-8") as f:
            f.write(json.dumps(newvault, indent="\t"))


if __name__ == "__main__":
    logging.basicConfig(filename="example.log", encoding="utf-8", level=logging.DEBUG)
    vault = Vault()
    definition = vault.get("edu.csun.www.admin.password", "csun")
    vault.add("testing3", "edu.csun.www.admin.password")
    vault = Vault.with_keyname("csun")
    definition = Vault.get_definition("edu.csun.www.admin.password", keyname="default")
    print(definition)
