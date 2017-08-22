import os

from click.testing import CliRunner


def test_fluorescence_to_concentration(fluorescence, concentration):
    from dobby.convert import fluorescence_to_concentration
    from dobby.io import _parse_fluorescence

    runner = CliRunner()
    result = runner.invoke(fluorescence_to_concentration, [fluorescence])
    assert result.exit_code == 0

    true = _parse_fluorescence(concentration, filetype='csv')
    assert result.output == true.to_csv()


def test_fluorescence_to_concentration_figures(fluorescence):
    from dobby.convert import fluorescence_to_concentration
    from dobby.util import filename_to_platename

    runner = CliRunner()
    platename = filename_to_platename(fluorescence)
    datatypes = 'concentration', 'fluorescence'

    with runner.isolated_filesystem():
        figure_folder = 'figure_folder'
        result = runner.invoke(fluorescence_to_concentration,
                               [fluorescence, '--figure-folder',
                                figure_folder])
        assert result.exit_code == 0

        for datatype in datatypes:
            heatmap_folder = os.path.join(figure_folder, 'concentration')
            pdf = os.path.join(heatmap_folder, datatype,
                               f'{platename}_{datatype}_heatmap.pdf')
            assert os.path.exists(pdf)
