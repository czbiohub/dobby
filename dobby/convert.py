import click
import pandas as pd
from scipy.stats import linregress

from .io import _parse_fluorescence
from .plot import _plot_regression, heatmap
from .util import filename_to_platename

STANDARDS_STR = '8,8,6,6,4,4,2,2,1,1,0.5,0.5,0.25,0.25,0,0'

STANDARDS = [8, 8, 6, 6, 4, 4, 2, 2, 1, 1, 0.5, 0.5, 0.025, 0.025, 0, 0]
STANDARDS_COL = 24
R_MINIMUM = 0.98


def _fluorescence_to_concentration(fluorescence, standards_col=STANDARDS_COL,
                                   standards=STANDARDS,
                                   platename=None, plot=True,
                                   output_folder='.', r_minimum=0.98):
    """Use standards column to regress and convert to concentrations
    
    """
    if isinstance(standards, str):
        # Make sure the standards use the same row names as the data
        standards = pd.Series(standards.split(','),
                              index=fluorescence.index).astype(float)

    import pdb; pdb.set_trace()
    means = fluorescence[standards_col].groupby(standards).mean()
    regressed = linregress(means.index, means)

    if regressed.rvalue < r_minimum:
        raise ValueError(
            f'{platename} Regression failed test: '
            f'{regressed.rvalue} < {r_minimum}')

    # Convert fluorescence to concentration
    concentrations = (fluorescence - regressed.intercept) / regressed.slope

    if plot:
        _plot_regression(means, regressed, platename)

        heatmap(fluorescence, platename, 'fluorescence', output_folder)
        heatmap(concentrations, platename, 'concentration', output_folder)

    return concentrations


@click.command(short_help='Converts plate fluorescence to concentrations')
@click.argument('filename', help='CSV of fluorescence')
@click.option('--standards-col', default=STANDARDS_COL, type=int,
              help='Column number containing concentration standards')
@click.option('--standards', default=STANDARDS_STR,
              help='Values of concentrations in the standards column')
@click.option('--figure-folder', default=None,
              help='Folder to create to put concentrations/, fluorescence/, '
                   'and regression/ subfolders into')
@click.option('--r-minimum', default=R_MINIMUM,
              help='Minimum Pearson correlation value for a plate to pass QC')
def fluorescence_to_concentration(filename, standards_col=STANDARDS_COL,
                                  standards=STANDARDS_STR, figure_folder=None,
                                  r_minimum=R_MINIMUM):
    """Convert plate fluorescence to concentrations by regression to standards
    
    \b
    Parameters
    ----------
    filename : str
        Name of the fluorescence CSV file
    standards_col : int, optional
        Integer number of the column that contains the concentration standards
        to use to convert fluorescence to concentrations using regression. 
        Default is column 24.
    standards : str
        Comma-separated values containing the concentration amounts in the 
        standards column. Default is '8,8,6,6,4,4,2,2,0.5,0.5,0.25,0.25,0,0'
    figure_folder : str
        Base folder to put a `fluorescence`, `concentration`, and `regression` 
        folders containing plots
    r_minimum : float
        Minimum Linear regression fit R-value (correlation coefficient) for a 
        plate to pass QC

    Returns
    -------
    Writes concentrations CSV to standard out
    """
    fluorescence = _parse_fluorescence(filename, 'csv')

    plot = False if figure_folder is None else True
    platename = filename_to_platename(filename)

    concentrations = _fluorescence_to_concentration(
        fluorescence, standards_col, standards, platename, plot,
        output_folder=figure_folder, r_minimum=r_minimum)

    # Write CSV to stdout
    click.echo(concentrations.to_csv(), nl=False)
