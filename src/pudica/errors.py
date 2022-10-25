class KeyfileNotFoundError(FileNotFoundError):
    pass


class KeyfileExistsError(FileNotFoundError):
    pass


class KeyfileLabelNotExistsError(ValueError):
    pass


class KeyfileLabelExistsError(ValueError):
    pass


class VaultEnvVarNotSetError(ValueError):
    pass


class VaultFileNotExistsError(FileNotFoundError):
    pass
