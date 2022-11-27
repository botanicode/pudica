# pudica

## About
Pudica is an encryption utility for Python designed with simplicity and reusability in mind.

## Principles
* **Opinionated is okay.** Part of keeping pudica simple is understanding where taking an opinionated approach is helpful. These stances then help with understanding the "rulse of the road".
* **Do what you do well.** Be helpful. Offer tools to make it easy to use and integrate pudica into workflows rather than offering a myriad of tools that spread efforts thin.
* **Make best practices easier.** Provide tools for things like key rotation and separation of duties. Make it easier to do the right thing rather than harder to do the wrong thing.

## Concepts
### Keyfile
Pudica relies on a **keyfile**, which stores key data, which include both the encryption key and key configuration settings in a single place. As such, this **keyfile** should be stored in a safe directory. It is strongly recommended to have only one **keyfile** if possible.

The default pudica **keyfile** location is `~/.pudica_keyfile`, but you can also save it in your `~/.ssh` folder if you like. You can then set the environment variable `PUDICA_KEYFILE` to be the path to the **keyfile**.

### Vaults
Pudica allows you to store encrypted values (known as ciphertext) in **vaults**. This helps with reusability and flexibility, and also helps enforce best practices. Multiple **vaults** can be added from different locations, too!

**Vaults** are read from the environment variable `PUDICA_VAULTS`, and are formatted the same way as the `PATH` environment variable; paths of one or more **vault** files separated by a colon (`:`).

A **vault** definition is composed of an **id**, a **keyname**, and a **ciphertext** value, and may look something like this:
```json
{
    "id": "com.example.login.username",
    "keyname": "default",
    "ciphertext": "gAAAAABjgTJiVlXuL55bKjAZ3xjk1kq1wzRop7lMSCZQ984fs6VNqKYVaO5TvWAEyGM4vs7HPrYdiE8vl-3bc9BdDOdFA37iLA=="
}
```
A combination of the **id** and the **keyname** are used to look up definitions, and the **ciphertext** value is the encrypted value for the associated definition. **id** values can be created in whatever format you like, but we prefer [reverse domain name notation](https://en.wikipedia.org/wiki/Reverse_domain_name_notation), particularly if you want to integrate it into your service or code.

The **keyfile** field is required, but it may have a `null` value. A **keyname** must be defined for key rotation to work correctly.

## Where did the name come from?
The name comes from *[Mimosa pudica](https://en.wikipedia.org/wiki/Mimosa_pudica)*, a plant that will fold in on itself when touched. Given that *pudica* roughly translates to "bashful" or "shy", it seemed a natural name for an encryption tool.

## Setup
To setup pudica, you will need:
1. A [**keyfile**](#keyfile)
    * This can either be stored at `~/.pudica_keyfile` or saved anywhere else and referred to using the `PUDICA_KEYFILE` environment variable
2. At least one [**vault**](#vaults)
    * All vault definitions need to be stored in the `PUDICA_VAULTS` environment variable. Multiple paths are separated with a colon (`:`)
