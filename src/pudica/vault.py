import os
from pudica.errors import *
from dataclasses import dataclass
import typing


@dataclass
class VaultDefinition:
    key: str
    label: typing.Optional[str]
    value: str


class Vault:

    __slots__ = ("paths", "definitions")

    def __init__(self):
        if "PUDICA_VAULTS" not in os.environ:
            raise VaultEnvVarNotSetError
        self.paths = os.environ["PUDICA_VAULTS"].split(":")
        errorpaths = list()
        for path in self.paths:
            if not os.path.exists(path):
                errorpaths.append(path)
        if len(errorpaths) > 0:
            raise VaultFileNotExistsError(", ".join(errorpaths))
        self.definitions = list()
        seen_definitions = set()
        for path in self.paths:
            with open(path, "r", encoding="utf-8") as f:
                for line in f.readlines():
                    components = line.split(":")
                    definition = VaultDefinition(*components)
                    fingerprint = ":".join(components[:2])
                    if fingerprint in seen_definitions:
                        continue
                    seen_definitions.add(fingerprint)
                    if len(definition.label) == 0:
                        definition.label = None
                    self.definitions.append(definition)

    def get_definition(
        self, key: str, label: typing.Optional[str] = None, get_default: bool = True
    ):
        key_definitions = [x for x in self.definitions if x.key == key]
        if len(key_definitions) == 0:
            raise VaultKeyLabelNotExistsError
        if label == None:
            unlabeled_definition = [x for x in key_definitions if x.label is None]
            if len(unlabeled_definition) > 0:
                return unlabeled_definition[0]
            default_definition = [x for x in key_definitions if x.label == "default"]
            if len(default_definition) > 0 and get_default is True:
                return default_definition[0]
            return key_definitions[0]
        else:
            mathcing_definition = [x for x in key_definitions if x.label == label]
            if len(mathcing_definition) > 0:
                return mathcing_definition[0]
        raise VaultKeyLabelNotExistsError
