```mermaid
classDiagram
      class Keychain{
        path
        keys
        _todict()
        _save()
        get_key()
        get_multikeys()
        add_key()
        new_key()
        default_key()
        key()$
        with_keyname()$
        multikeys()$
        generate()$
      }
      class Vault{
        paths
        definitions
        get()
        add()
        with_keyname()$
        get_definition()$
        generate()$
      }
      class Encryptor{
        _make_fernets()$
        encrypt_multi()$
        encrypt_bytes()$
        encrypt_str()$
        encrypt()$
        encrypt_file()$
        decrypt_multi()$
        decrypt_bytes()$
        decrypt_str()$
      }
      class Pudica{
        __keychain
        __vault
        load_keychain()
        load_vault()
        encrypt()
        decrypt()
        generate_keychain()$
        generate_vault()$
      }
      class VaultDefinition{
        id
        keyname
        ciphertext
        vaultpath
        fromdict()$
        todict()
        new()$
      }
      class Key{
        keyname
        fernet
        multikey
        updated
        fromdict()$
        todict()
        new()$
      }
      Keychain "1" o-- "*" Key
      Vault "1" o-- "*" VaultDefinition
      Pudica -- Keychain
      Pudica -- Encryptor
      Pudica -- Vault
```