# pudica

## About
Pudica is an encryption utility for Python designed with simplicity and reusability in mind.

## Principles
* **Opinionated is okay.** Part of keeping pudica simple is understanding where taking an opinionated approach is helpful. These stances then help with understanding the "rulse of the road".
* **Do what you do well.** Be helpful. Offer tools to make it easy to use and integrate pudica into workflows rather than offering a myriad of tools that spread efforts thin.
* **Make best practices easier.** Provide tools for things like key rotation and separation of duties. Make it easier to do the right thing rather than harder to do the wrong thing.

## Concepts
### Keyfile
Pudica relies on a **keyfile**, which stores key definitions, which include the encryption key and key configuration settings in a single place. As such, this **keyfile** should be stored in a safe directory. It is strongly recommended to have one **keyfile** if possible.

The default pudica **keyfile** location is `~/.pudica_keyfile`, but you can also save it in your `~/.ssh` folder if you like. You can then set the environment variable `PUDICA_KEYFILE` to be the path to the **keyfile**.

### Vaults
Pudica allows you to store encrypted values in **vaults**. This helps with reusability and flexibility, and also helps enforce best practices. Multiple **vaults** can be added from different locations, too!

**Vaults** are read from the environment variable `PUDICA_VAULTS`, and are formatted the same way as the `PATH` environment variable; paths separated by a colon (`:`).

A **vault** definition is composed of a **key**, a **label** (optional), and a **value**, and may look something like this:
```
key:label:gAAAAABjWBNz4TJ_5FTuOvP_IcUpJbjff0v2vXplWQ3gtl0TFzEmo_sY25_28_Xw79tmspUMAuvRLOG-wAMjbnyM_8Wav3gGxqJPk8yiUw615lSCB5c1pjY=
```
The **key** is how you look up definitions, and the **value** is the encrypted value for the associated **key**. The **label** is optional, but will tell pudica which **keyfile** to use. Having a **label** required for key rotation, and is handy if the **keyfile** definition for the given **label** does not allow for **multikey**.

## Where did the name come from?
The name comes from *[Mimosa pudica](https://en.wikipedia.org/wiki/Mimosa_pudica)*, a plant that will fold in on itself when touched. Given that *pudica* roughly translates to "bashful" or "shy", it seemed a natural name for an encryption tool.

## Setup
To setup pudica, you will need:
1. A [**keyfile**](#keyfile)
    * This can either be stored at `~/.pudica_keyfile` or saved anywhere else and referred to using the `PUDICA_KEYFILE` environment variable
2. At least one [**vault**](#vaults)
    * All vault definitions need to be stored in the `PUDICA_VAULTS` environment variable. Multiple paths are separated with a colon (`:`)
