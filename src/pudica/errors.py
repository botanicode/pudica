class KeyfileNotFoundError(FileNotFoundError):
    pass


class KeyfileExistsError(FileNotFoundError):
    pass


class KeyfileLabelNotExistsError(ValueError):
    pass


class KeyfileLabelExistsError(ValueError):
    pass


class KeyfileWriteFailureError(ValueError):
    pass


class VaultEnvVarNotSetError(ValueError):
    pass


class VaultFileNotExistsError(FileNotFoundError):
    pass


class VaultKeyLabelNotExistsError(ValueError):
    pass


class KeyfileKeynameNotExistsError(ValueError):
    pass


class VaultItemNotExistsError(ValueError):
    pass


class VaultItemExistsError(ValueError):
    pass


class VaultDefinitionNotExistsError(ValueError):
    pass
