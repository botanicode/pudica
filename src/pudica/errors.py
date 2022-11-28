class KeyMalformedError(ValueError):
    pass


class KeychainNotFoundError(FileNotFoundError):
    pass


class KeychainExistsError(IOError):
    pass


class KeychainLabelNotExistsError(ValueError):
    pass


class KeychainLabelExistsError(ValueError):
    pass


class KeychainWriteFailureError(IOError):
    pass


class VaultEnvVarNotSetError(ValueError):
    pass


class VaultFileNotExistsError(FileNotFoundError):
    pass


class VaultKeyLabelNotExistsError(ValueError):
    pass


class KeychainKeynameNotExistsError(ValueError):
    pass


class VaultItemNotExistsError(ValueError):
    pass


class VaultItemExistsError(ValueError):
    pass


class VaultDefinitionNotExistsError(ValueError):
    pass


class VaultDefinitionMalformedError(ValueError):
    pass


class VaultMutateNotSyntheticError(ValueError):
    pass


class VaultUpsertSyntheticError(ValueError):
    pass


class VaultWriteFailureError(IOError):
    pass

class VaultExistsError(IOError):
    pass