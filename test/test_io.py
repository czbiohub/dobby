import os

from click.testing import CliRunner
import pandas as pd
import pytest


def test_parse_fluorescence(filename):
    from dobby.io import parse_fluorescence, _parse_fluorescence

    runner = CliRunner()
    result = runner.invoke(parse_fluorescence, [filename])
    assert result.exit_code == 0

    csv = filename.replace('.txt', '.csv')
    true = _parse_fluorescence(csv, filetype='csv')
    assert result.output == true.to_csv()