import os

import click

from dobby.dobby.cherrypick import BLANKS_COL, _cherrypick_wells
from .convert import _fluorescence_to_concentration, STANDARDS_COL, \
    STANDARDS_STR
from .io import _parse_fluorescence
from .util import maybe_make_directory, _parse_standards


def _transform_to_pick_list(good_cells, plate_name, mouse_id, datatype,
                            output_folder='.'):
    # Convert 2d matrix into tall, tidy dataframe
    echo_picks = good_cells.unstack().reset_index().dropna()
    echo_picks = echo_picks.rename(
        columns={'level_0': 'column_number', 'level_1': 'row_letter',
                 0: 'concentration'})
    echo_picks['well'] = echo_picks.apply(
        lambda x: '{row_letter}{column_number}'.format(**x),
        axis=1)
    echo_picks['plate'] = plate_name
    echo_picks['mouse_id'] = mouse_id
    echo_picks['name'] = echo_picks.apply(
        lambda x: '{well}-{plate}-{mouse_id}-1'.format(**x),
        axis=1)
    csv = os.path.join(output_folder, datatype, f'{plate_name}_echo.csv')
    maybe_make_directory(csv)
    echo_picks.to_csv(csv, index=False)
    print(f'Wrote {datatype} ECHO pick list to {csv}')
    return csv


@click.command('make_echo_pick_lists',
               short_help="Convert concentrations --> ECHO pick list")
@click.argument('filename')
@click.argument('plate_name')
@click.argument('mouse_id')
@click.option('--filetype', default='txt')
# @click.option('--metadata', default='~/maca-dash/MACA_Metadata\ -\ 384_well_plates.csv ')
@click.option('--standards-col', default=STANDARDS_COL, type=int)
@click.option('--blanks_col', default=BLANKS_COL)
@click.option('--standards', default=STANDARDS_STR)
@click.option('--plot', is_flag=True)
@click.option('--output-folder', default='.')
def make_echo_pick_lists(filename, plate_name, mouse_id, filetype='txt',
                         # metadata='~/maca-dash/MACA_Metadata\ -\ 384_well_plates.csv ',
                         standards_col=STANDARDS_COL, blanks_col=BLANKS_COL,
                         standards=STANDARDS_STR,
                         plot=True, output_folder='.'):
    """Transform plate of cDNA fluorescence to ECHO pick list
    
    \b
    Parameters
    ----------
    filename : str
        Name of the cDNA fluorescence 384 well QC output
    plate_name
    mouse_id
    filetype
    standards_col
    blanks_col
    standards
    plot
    output_folder

    Returns
    -------

    """
    standards = _parse_standards(standards)
    # plate_name = filename_to_plate_name(filename)
    # mouse_id = plate_name_to_mouse_id(plate_name)

    fluorescence = _parse_fluorescence(filename, filetype)

    concentrations = _fluorescence_to_concentration(
        fluorescence, standards_col, standards, plate_name, plot,
        output_folder=output_folder)
    good_cells = _cherrypick_wells(concentrations, blanks_col, plate_name,
                                   output_folder=output_folder,
                                   plot=plot)

    _transform_to_pick_list(good_cells, plate_name, mouse_id, 'cherrypicked',
                            output_folder=output_folder)
    _transform_to_pick_list(concentrations, plate_name, mouse_id,
                            'non_cherrypicked', output_folder=output_folder)


