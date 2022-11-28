import logging
from typing import Optional, List, Dict, Any
import os
from pudica.errors import (
    VaultEnvVarNotSetError,
    VaultDefinitionNotExistsError,
    VaultDefinitionMalformedError,
    VaultMutateNotSyntheticError,
    VaultUpsertSyntheticError,
    VaultWriteFailureError,
    VaultExistsError,
)
import json
from dataclasses import dataclass
import shutil


@dataclass
class VaultDefinition:
    id: Optional[str] = None
    keyname: Optional[str] = None
    ciphertext: Optional[str] = None
    vault: Optional["Vault"] = None

    def __str__(self) -> str:
        return f"VaultDefinition({self.id}: encrypted using {self.keyname})"

    def __repr__(self) -> str:
        return self.__str__()

    @staticmethod
    def fromdict(d: Dict[str, Any]) -> "VaultDefinition":
        if "id" not in d or "ciphertext" not in d:
            logging.error(f"Vault definition missing either id or ciphertext value")
            raise VaultDefinitionMalformedError
        return VaultDefinition(
            id=d["id"],
            keyname=d.get("keyname", None),
            ciphertext=d["ciphertext"],
        )

    def todict(self) -> Dict[str, Any]:
        if self.id is None or self.ciphertext is None:
            logging.error(
                f"Can't convert VaultDefinition to dict without an id and a ciphertext value"
            )
            raise VaultDefinitionMalformedError
        return {"id": self.id, "keyname": self.keyname, "ciphertext": self.ciphertext}


class Vault:
    __slots__ = ("path", "definitions", "is_synthetic")

    def __init__(self, path: Optional[str] = None) -> None:
        self.is_synthetic: bool = False
        self.path: Optional[str] = None
        if path is None:
            logging.debug(f"No path provided, creating a synthetic vault")
            self.is_synthetic = True
            return
        self.path: str = path
        logging.debug(f"Reading vault at `{self.path}`...")
        self.definitions: List[VaultDefinition] = list()
        with open(path, "r", encoding="utf-8") as f:
            vault_data: Dict[str, Any] = json.loads(f.read())
            for definition in vault_data.get("definitions", list()):
                vaultdefinition = VaultDefinition.fromdict(definition)
                vaultdefinition.vault = self
                self.definitions.append(vaultdefinition)
        logging.debug(
            f"Loaded {len(self.definitions)} definition(s) from vault at `{self.path}`"
        )

    def get_ids(self, id: str) -> List[VaultDefinition]:
        return [definition for definition in self.definitions if definition.id == id]

    def get_keynames(self, keyname: str) -> List[VaultDefinition]:
        return [
            definition
            for definition in self.definitions
            if definition.keyname == keyname
        ]

    def filter_ids(self, id: str) -> int:
        if self.is_synthetic is False:
            logging.error(f"Can not filter on a non-sythetic vault")
            raise VaultMutateNotSyntheticError
        beginning_count: int = len(self.definitions)
        self.definitions = [defn for defn in self.definitions if defn.id == id]
        return beginning_count - len(self.definitions)

    def filter_keynames(self, keyname: Optional[str]) -> int:
        if self.is_synthetic is False:
            logging.error(f"Can not filter on a non-sythetic vault")
            raise VaultMutateNotSyntheticError
        beginning_count: int = len(self.definitions)
        self.definitions = [
            defn for defn in self.definitions if defn.keyname == keyname
        ]
        return beginning_count - len(self.definitions)

    def add_definitions(self, definitions: List[VaultDefinition]) -> int:
        if self.is_synthetic is False:
            logging.error(f"Can not add definitions to a non-sythetic vault")
            raise VaultMutateNotSyntheticError
        self.definitions += definitions
        return len(self.definitions)

    def synthetic(self) -> "Vault":
        vault: Vault = Vault()
        vault.add_definitions(self.definitions)
        return vault

    def upsert(self, definition: VaultDefinition) -> bool:
        if self.is_synthetic is True:
            logging.error(f"Can not upsert on a sythetic vault")
            raise VaultUpsertSyntheticError
        for pos, defn in enumerate(self.definitions):
            if defn.id == definition.id and defn.keyname == definition.keyname:
                self.definitions[pos] = definition
                return True
        definition.vault = self
        return self._save()

    def _todict(self) -> Dict[str, Any]:
        return {"definitions": [defn.todict() for defn in self.definitions]}

    def _save(self, delete_backup: bool = True) -> bool:
        logging.debug(f"Saving vault at path `{self.path}`...")
        logging.debug(f"Backing up vault...")
        backup_path: str = f"{self.path}_backup"
        shutil.copyfile(self.path, backup_path)
        errored: bool = False
        try:
            logging.debug(f"Writing updated vault...")
            with open(self.path, "w", encoding="utf-8") as f:
                f.write(json.dumps(self._todict(), indent="\t"))
            logging.debug(f"Updated vault written")
        except:
            logging.error(f"Writing updated vault failed")
            logging.error(f"Restoring original vault")
            shutil.copyfile(backup_path, self.path)
            errored = True
        if delete_backup:
            os.unlink(backup_path)
            logging.debug(f"Backup vault deleted")
        if errored:
            raise VaultWriteFailureError
        logging.debug(f"Vault update complete")
        return True

    @staticmethod
    def generate(path: str, overwrite: bool = False) -> 'Vault':
        logging.debug(f"Generating new vault at path `{path}`...")
        if os.path.exists(path) and overwrite is False:
            logging.error(f"Vault already exists at `{path}`")
            raise VaultExistsError
        newvault = {"definitions": list()}
        with open(path, "w", encoding="utf-8") as f:
            f.write(json.dumps(newvault, indent="\t"))
        logging.debug(f"New vault generated at `{path}`")
        return Vault(path)


class VaultManager:
    __slots__ = "vaults"

    def __init__(self, paths: Optional[str] = None) -> None:
        logging.debug("Reading vault(s)...")
        working_paths: Optional[str] = paths
        if working_paths is None:
            logging.debug(
                'Vault paths not provided in Vault.__init__(), checking "PUDICA_VAULTS" environment variable...'
            )
            if "PUDICA_VAULTS" not in os.environ:
                logging.error(
                    'Vault paths not provided in Vault.__init__(), "PUDICA_VAULTS" environment variable not present'
                )
                raise VaultEnvVarNotSetError
            working_paths = os.environ["PUDICA_VAULTS"]
            logging.debug(
                f'Reading vault(s) from "PUDICA_VAULTS" environment variable: `{working_paths}`'
            )
        else:
            logging.debug(f"Reading vault(s) from provided paths: `{working_paths}`")
        self.vaults: List[Vault] = list()
        for path in working_paths.split(":"):
            self.vaults.append(Vault(path))
        logging.debug(f"Loaded {len(self.vaults)} vault(s)")

    def get(
        self,
        id: Optional[str] = None,
        keyname: Optional[str] = None,
        explicit_keyname: bool = False,
    ) -> VaultDefinition:
        logging.debug(
            f"Finding vault definition with id `{'*' if id is None else id}` and keyname `{'null' if keyname is None else keyname}`..."
        )
        synthetic_vault: Vault = Vault()
        for vault in self.vaults:
            if id is not None:
                synthetic_vault.add_definitions(vault.get_ids(id))
            else:
                synthetic_vault.add_definitions(vault.definitions)
            if explicit_keyname is True or keyname is not None:
                synthetic_vault.filter_keynames(keyname)
        if len(synthetic_vault.definitions) < 1:
            raise VaultDefinitionNotExistsError
        logging.debug(
            f"Found {len(synthetic_vault.definitions)} matching definition(s)"
        )
        return synthetic_vault.definitions[0]

    def upsert_definition(
        self,
        definition: VaultDefinition,
        vault: Optional[Vault] = None
    ) -> bool:
        logging.debug(f"Adding definition with id `{definition.id}` to vault...")
        working_vault: Optional[Vault] = definition.vault
        if working_vault is None: 
            working_vault = vault
        if working_vault is None:
            working_vault = self.vaults[0]
        logging.debug(f"Adding definition with id `{definition.id}` to vault at path `{working_vault.path}`...")
        return working_vault.upsert(definition)

    def upsert(self, id: str, ciphertext: str, keyname: Optional[str], vault: Optional[Vault]) -> bool:
        working_definition = VaultDefinition(id, keyname, ciphertext, vault)
        return self.upsert_definition(working_definition)

    def synthetic_vault(self) -> Vault:
        synthetic_vault: Vault = Vault()
        for vault in self.vaults:
            synthetic_vault.add_definitions(vault.definitions)
        return synthetic_vault

    @staticmethod
    def with_keyname(keyname, paths: Optional[str] = None) -> "VaultManager":
        vm = VaultManager(paths=paths)
        synthetic_vault = vm.synthetic_vault()
        synthetic_vault.filter_keynames(keyname)
        vm.vaults = [synthetic_vault]
        return vm

    @staticmethod
    def definition(id: str, keyname: Optional[str] = None) -> VaultDefinition:
        vm = VaultManager()
        return vm.get(id, keyname)
