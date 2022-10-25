import os
from pudica.errors import *


class Vault:

    __slots__ = "paths"

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
