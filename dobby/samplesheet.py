import os
import glob

import click
import pandas as pd

from .util import maybe_make_directory

TEMPLATE_SAMPLE_ID_COL = 'SampleID'

TEMPLATE_FOLDER = os.path.join(os.path.dirname(__file__),
                               'samplesheet_templates')

AVAILABLE_TEMPLATES = [x.split('.csv')[0] for x in
                       glob.iglob(os.path.join(TEMPLATE_FOLDER, '*.csv'))]

AVAILABLE_TEMPLATES_STR = ', '.join(['"x"' for x in AVAILABLE_TEMPLATES])


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

    input_df = pd.read_csv(filename)
    samples = input_df[sample_id_col]

    template = _get_template(template_name)
    template[TEMPLATE_SAMPLE_ID_COL] = samples

    basename = os.path.basename(filename)
    csv = os.path.join(output_folder,
                       basename.replace('.csv', '_samplesheet.csv'))
    maybe_make_directory(csv)
    template.to_csv(csv)
    print(f'Wrote {csv}')