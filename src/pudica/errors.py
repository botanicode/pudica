class KeyMalformedError(ValueError):
    pass


class KeychainNotFoundError(FileNotFoundError):
    pass


class KeychainExistsError(FileNotFoundError):
    pass


class KeychainLabelNotExistsError(ValueError):
    pass


class KeychainLabelExistsError(ValueError):
    pass


class KeychainWriteFailureError(ValueError):
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
