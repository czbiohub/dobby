import os

import click
from click.testing import CliRunner
import pytest

@pytest.fixture
def data_folder():
    dirname = os.os.path.abspath(__file__)
    return os.path.join(dirname, 'data')


@pytest.fixture
def filename(data_folder):
    return os.path.join(data_folder, 'MAA000154.txt')




def test_hello_world():
    @click.command()
    @click.argument('name')
    def hello(name):
        click.echo('Hello %s!' % name)

    runner = CliRunner()
    result = runner.invoke(hello, ['Peter'])
    assert result.exit_code == 0
    assert result.output == 'Hello Peter!\n'