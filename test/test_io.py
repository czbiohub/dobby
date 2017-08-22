import os

import click
from click.testing import CliRunner


def test_parse_fluorescence(raw_fluorescence, fluorescence):
    from dobby.io import parse_fluorescence, _parse_fluorescence

    runner = CliRunner()
    result = runner.invoke(parse_fluorescence, [raw_fluorescence])
    assert result.exit_code == 0

    true = _parse_fluorescence(fluorescence, filetype='csv')
    assert result.output == true.to_csv()


def test_parse_fluorescence_heatmap(raw_fluorescence, capsys):
    from dobby.io import parse_fluorescence, _parse_fluorescence
    from dobby.util import filename_to_platename

    heatmap_folder = 'figure_folder'
    datatype = 'fluorescence'
    platename = filename_to_platename(raw_fluorescence)

    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(parse_fluorescence,
                               [raw_fluorescence, '--figure-folder',
                                heatmap_folder])
        out, err = capsys.readouterr()
        assert result.exit_code == 0

        pdf = os.path.join(heatmap_folder, 'fluorescence',
                           f'{platename}_{datatype}_heatmap.pdf')
        assert os.path.exists(pdf)
