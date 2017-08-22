import sys

import click

from .io import _parse_fluorescence
from .plot import heatmap
from .util import filename_to_platename

BLANKS_COL = 23


def _cherrypick_wells(concentrations, blanks_col, platename,
                      plot=True,
                      output_folder='.'):
    """Use blanks column to determine whether a well has enough fluorescence"""

    average_blanks = concentrations[blanks_col].mean()
    std_blanks = concentrations[blanks_col].std()

    # Minimum threshold: One standard deviation away from the mean
    avg_std = average_blanks + std_blanks

    is_cell_good = concentrations > avg_std
    n_good_cells = is_cell_good.sum().sum()
    sys.stderr.write(
        f'{platename} has {n_good_cells} wells passing '
        f'concentration QC\n')
    good_cells = concentrations[is_cell_good]

    without_standards_or_blanks = good_cells.loc[:, :(blanks_col - 1)]

    if plot:
        heatmap(without_standards_or_blanks, platename,
                 'without_standards_or_blanks', output_folder)

    return without_standards_or_blanks


@click.command(short_help="Choose wells with fluorescence higher than average"
                          " blank well")
@click.argument('filename')
@click.option('--blanks_col', default=BLANKS_COL, type=int)
@click.option('--figure-folder', default=None)
def cherrypick_wells(filename, blanks_col, figure_folder='.'):
    concentrations = _parse_fluorescence(filename, 'csv')

    plot = False if figure_folder is None else True
    platename = filename_to_platename(filename)
    cherrypicked = _cherrypick_wells(concentrations, blanks_col, platename,
                                     plot, figure_folder)

    # Write CSV to stdout
    click.echo(cherrypicked.to_csv(), nl=False)
