import os
import glob

import click
import pandas as pd

from .util import maybe_make_directory

TEMPLATE_SAMPLE_ID_COL = 'SampleID'
TEMPLATE_SAMPLE_NAME_COL = 'Sample_Name'

TEMPLATE_FOLDER = os.path.join(os.path.dirname(__file__),
                               'samplesheet_templates')

AVAILABLE_TEMPLATES = [os.path.basename(x).split('.csv')[0] for x in
                       glob.iglob(os.path.join(TEMPLATE_FOLDER, '*.csv'))]

AVAILABLE_TEMPLATES_STR = ', '.join([f'"{x}"' for x in AVAILABLE_TEMPLATES])


def _get_template(template_name):
    try:
        csv = os.path.join(TEMPLATE_FOLDER, f'{template_name}.csv')
        return pd.read_csv(csv)
    except FileNotFoundError:
        raise FileNotFoundError(f'{template_name} is not a valid template. '
                                f'Available templates are: '
                                f'{AVAILABLE_TEMPLATES_STR}')


@click.command(short_help="Create an Illumina sample sheet using a template")
@click.argument('filename')
@click.argument('template_name')
@click.option('--sample-id-col', default="Combined name",
              help='Name of the column containing the sample ID to be used in'
                   ' the sample sheet')
@click.option('--output-folder', default='.',
              help='Where to output the sample sheet')
def samplesheet(filename, template_name, sample_id_col, output_folder):
    """Create sample sheets from included templates
    
    Example:
    $ dobby samplesheet --output-folder test_samplesheet \
        test_aggregate/echo_picklist_00015.csv XT-C-04
        
    Parameters
    ----------
    filename : str
        Name of the file with the samples sorted in correct order, containing 
        a column specified by --sample-id-col that has the sample names
    template_name : str
        Name of a sample sheet template. Available templates:
        "XT-C-01", "XT-C-02", "XT-C-03", "XT-C-04", "XT-C-05", "XT-C-06", 
        "XT-C-07", "XT-C-08", "XT-C-09", "XT-C-10", "XT-C-11", "XT-C-12", 
        "XT-C-13", "XT-C-14", "XT-C-15", "XT-C-16", "XT-C-17", "XT-C-18", 
        "XT-C-19", "XT-C-20", "XT-C-21", "XT-C-22", "XT-C-23"

    Returns
    -------
    Writes a sample sheet to the output folder, with the name 
    $filename_samplesheet.csv, where $filename means the input filename
    """

    input_df = pd.read_csv(filename)
    samples = input_df[sample_id_col]

    template = _get_template(template_name)
    template[TEMPLATE_SAMPLE_ID_COL] = samples
    template[TEMPLATE_SAMPLE_NAME_COL] = samples

    basename = os.path.basename(filename)
    csv = os.path.join(output_folder,
                       basename.replace('.csv', '_samplesheet.csv'))
    maybe_make_directory(csv)
    template.to_csv(csv, index=False)
    print(f'Wrote {csv}')