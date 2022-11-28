from pudica import Pudica
import click
from typing import Optional


@click.group()
def cli():
    pass


@cli.command()
@click.option("--keychain/--no-keychain", default=False)
@click.option("--keychain-path", default=None)
@click.option("--vault/--no-vault", default=False)
@click.option("--vault-path", default=None)
def generate(
    keychain: bool, keychain_path: Optional[str], vault: bool, vault_path: Optional[str]
):
    if keychain:
        if keychain_path is not None:
            Pudica.generate_keychain(keychain_path)
        else:
            Pudica.generate_keychain()
    if vault:
        if vault_path is not None:
            Pudica.generate_vault(vault_path)
        else:
            Pudica.generate_vault()


@cli.command()
@click.option("--keyname", "-k")
def new_key(keyname):
    with Pudica() as pu:
        pu._keychain.new_key(keyname)


@cli.command()
@click.option("--keyname", "-k", default=None)
@click.option("--id", "-i", default=None)
@click.option("--value", "-v")
def add_definition(keyname, id, value):
    with Pudica() as pu:
        definition = pu.encrypt(value, keyname=keyname, id=id)
        pu._vault.upsert_definition(definition)
        click.echo(f"item added with id {definition.id}")


@cli.command()
@click.option("--keyname", "-k", default=None)
@click.option("--id", "-i", default=None)
@click.option("--value", "-v", prompt=True, hide_input=True)
def add_secret(keyname, id, value):
    click.echo(value)
    with Pudica() as pu:
        definition = pu.encrypt(value, keyname=keyname, id=id)
        pu._vault.upsert_definition(definition)
        click.echo(f"item added with id {definition.id}")


if __name__ == "__main__":
    cli()
