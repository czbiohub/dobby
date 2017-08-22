import string

import click
import pandas as pd

from .plot import heatmap
from .util import filename_to_platename


SKIP_FOOTER = 409
PARSE_COLS = 'C:Z'
SKIPROWS = 2
NROWS = 16
ENCODING = 'UTF-16'
USECOLS = range(2, 26)

EXCEL_KWS = dict(skip_footer=SKIP_FOOTER, parse_cols=PARSE_COLS)
TABLE_KWS = dict(nrows=NROWS, encoding=ENCODING, skiprows=SKIPROWS,
                 usecols=USECOLS)
CSV_KWS = dict(index_col=0)


def _parse_fluorescence(filename, filetype='txt', kwargs=None):
    kwargs = {} if kwargs is None else kwargs
    filetype = filetype.lower()

    if filetype == 'txt' or filetype.startswith('tab'):
        parser = pd.read_table
        kwargs.update(TABLE_KWS)
    elif filetype == 'csv':
        parser = pd.read_csv
        kwargs.update(CSV_KWS)
    else:
        raise ValueError(f"'{filetype}' is not a supported file type. "
                         "Only 'txt' and 'csv' are supported")
    fluorescence = parser(filename, **kwargs)
    fluorescence.columns = fluorescence.columns.astype(int)
    fluorescence.index = list(string.ascii_uppercase[:len(fluorescence.index)])
    return fluorescence


@click.command('parse_fluorescence',
               short_help='Extracts fluorescence data from plate reader '
                          'output and writes to CSV')
@click.argument('filename')
@click.option('--filetype', default='txt')
@click.option('--kwargs', default=None)
@click.option('--figure-folder', default=None)
def parse_fluorescence(filename, filetype='txt', kwargs=None,
                       figure_folder=None):
    """Extracts fluorescence data from plate reader output and saves to CSV
    
    Arguments
    ---------
    filename : str
        Name of the fluorescence file to read. Assumed to be the name of the 
        plate
    filetype : 'txt' | 'table' | 'csv', optional
        Format of the file to expect. If "csv", then assumes that this file 
        was already properly parsed by dobby

    Options
    -------
    kwargs : dict
        Other keyword arguments to pass to pandas.read_csv
    heatmap_folder : str
        Name of the folder to write a heatmap of the fluorescence to

    Outputs
    -------
    fluorescence comma-separated variables to standard out
    """
    kwargs = eval(kwargs) if kwargs is not None else kwargs

    fluorescence = _parse_fluorescence(filename, filetype, kwargs)

    if figure_folder is not None:
        platename = filename_to_platename(filename)
        heatmap(fluorescence, platename, 'fluorescence', figure_folder)

    # Write CSV to stdout
    click.echo(fluorescence.to_csv(), nl=False)
