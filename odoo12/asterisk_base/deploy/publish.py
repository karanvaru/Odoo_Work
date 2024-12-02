#!/usr/bin/python
import click
import subprocess

VERSION = '1.1'


@click.command()
@click.option('--version')
@click.option('--latest', is_flag=True)
@click.option('--push', is_flag=True)
@click.option('--no-cache', is_flag=True)
def build(version, push, latest, no_cache):
    if not version:
        version = VERSION
    # Build AMD63
    subprocess.check_call(
        'docker buildx build {} --platform linux/amd64,linux/arm/v7 '
        '-t odooist/asterisk-server:{} {} .'.format(
            '' if not no_cache else '--no-cache', version,
            '' if not push else '--push'), shell=True)
    if latest:
        subprocess.check_call(
            'docker buildx build {} --platform linux/amd64,linux/arm/v7 '
            '-t odooist/asterisk-server:latest {} .'.format(
                '' if not no_cache else '--no-cache',
                '' if not push else '--push'), shell=True)

if __name__ == '__main__':
    build()
