import os
import string
import warnings
import time

import click
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import linregress
import seaborn as sns

sns.set(context='paper')

with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    mpl.use('agg')

from .util import maybe_make_directory

N_EXTRA_LINES = 409
COLUMNS_TO_PARSE = 'C:Z'
ROWS_TO_SKIP = 2

STANDARDS_STR = '8,8,6,6,4,4,2,2,1,1,0.5,0.5,0.25,0.25,0,0'

STANDARDS = [8, 8, 6, 6, 4, 4, 2, 2, 1, 1, 0.5, 0.5, 0.25, 0.25, 0, 0]
STANDARDS_COL = 24
BLANKS_COL = 23

CONCENTRATIONS_MINIMUM = 0.7
CONCENTRATIONS_MAXIMUM = 10
R_MINIMUM = 0.98

FLAGGED = 'flagged'
FLAG_FOLDER_PREFIX = 'flag'
RECORD_FILE = 'record_plate_flagged_timestamp.csv'


def _parse_standards(standards_str):
    values = standards_str.split(',')
    index = list(string.ascii_uppercase[:len(values)])
    return pd.Series(values, index=index).astype(float)


def _parse_fluorescence(filename, filetype):
    filetype = filetype.lower()

    kwargs = dict(skiprows=ROWS_TO_SKIP)
    if filetype == 'excel':
        parser = pd.read_excel
        kwargs.update(
            dict(skip_footer=N_EXTRA_LINES, parse_cols=COLUMNS_TO_PARSE))
    elif filetype == 'csv':
        parser = pd.read_csv

        # Use columns 1-24 (25 is not included)
        kwargs['usecols'] = range(1, 25)
        kwargs.update
    elif filetype == 'txt' or filetype == 'table':
        parser = pd.read_table
        kwargs.update(dict(nrows=16, encoding='utf-16', skiprows=2,
                           usecols=range(2, 26)))
    else:
        raise ValueError(f"'{filetype}' is not a supported file type. "
                         "Only 'csv' and 'excel' are supported")
    fluorescence = parser(filename, **kwargs)
    fluorescence.columns = fluorescence.columns.astype(int)
    fluorescence.index = list(string.ascii_uppercase[:len(fluorescence.index)])
    return fluorescence


def _plot_regression(means, regressed, plate_name, output_folder='.'):
    fig, ax = plt.subplots()
    means.name = 'Means of standard concentrations'
    y = pd.Series(regressed.slope * means.index + regressed.intercept,
                  index=means.index,
                  name='Regression')

    ax.plot(means, 'o-', label=means.name)
    ax.plot(y, 'o-', label=y.name)
    ax.legend()

    # :.5 indicates 5 decimal places
    plt.title(f'$R^2$ = {regressed.rvalue:.5}')

    pdf = os.path.join(output_folder, 'regression',
                       f'{plate_name}_regression_lines.pdf')
    maybe_make_directory(pdf)
    fig.savefig(pdf)
    fig.tight_layout()
    print(f'{plate_name}: Wrote regression plot to {pdf}')
    return pdf


def _heatmap(data, plate_name, datatype, output_folder, title_suffix=None,
             drop_standards=True, **kwargs):
    """Draw a heatmap of values

    Parameters
    ----------
    data : pandas.DataFrame
        The 384-well fluorescence or concentration to plot
    plate_name : str
        Name of the plate
    datatype : str
        Type of data, e.g. "fluorescence" or "concentration"
    output_folder : str
        Location of the folder to output
    title_suffix : str
        Additional information to add to the title
    drop_standards : bool
        If True, then remove the 24th column which contains standard
        concentrations for plotting
    kwargs
        Any other keyword arguments for seaborn.heatmap

    Returns
    -------
    pdf : str
        Filename of the heatmap
    """
    if drop_standards:
        no_standards = data.drop(STANDARDS_COL, axis=1, errors='ignore')
    else:
        no_standards = data

    title_suffix = '' if title_suffix is None else title_suffix
    fig, ax = plt.subplots(figsize=(8, 4))
    sns.heatmap(no_standards, annot=True, ax=ax, annot_kws={"size": 8},
                **kwargs)
    plt.title(f'{plate_name} {datatype}' + title_suffix)
    pdf = os.path.join(output_folder, datatype,
                       f'{plate_name}_{datatype}_heatmap.pdf')
    maybe_make_directory(pdf)
    fig.tight_layout()
    fig.savefig(pdf)
    print(f'{plate_name}: Wrote {datatype} heatmap to {pdf}')
    return pdf


def _fluorescence_to_concentration(fluorescence, standards_col, standards,
                                   output_folder='.', r_minimum=R_MINIMUM,
                                   inner=True):
    """Use standards column to regress and convert to concentrations"""
    standards = pd.Series(standards, index=fluorescence.index)

    means = fluorescence[standards_col].groupby(standards).mean()
    # Don't use the very first or very last concentrations for regressing
    if inner:
        means = pd.Series(means.values[1:-1], means.index[1:-1])
    regressed = linregress(means.index, means)

    # Convert fluorescence to concentration
    concentrations = (fluorescence - regressed.intercept) / regressed.slope

    if regressed.rvalue < r_minimum:
        print(f'\tRegression failed test: {regressed.rvalue} < {r_minimum}')
        output_folder = os.path.join(output_folder, 'failed')

    return concentrations, means, regressed

def record_flagged_plate_and_determine_folder(output_folder,platename):
    record_file_dir = os.path.join(output_folder, FLAGGED)
    record_file_path = os.path.join(record_file_dir, RECORD_FILE)
    number_of_times_flagged = 1

    #if file doesn't exist make file and add line record for platename
    if not os.path.exists(record_file_path):

        if not os.path.exists(record_file_dir):
            os.makedirs(record_file_dir)

        with open(record_file_path, 'w') as record_file:
            record_file.write(platename + ',' + timestamp() + '\n')

    else: #file does exist
        with open(record_file_path, 'r') as record_file:
            record = record_file.readlines()

        plate_in_file = False
        for index_line, line in enumerate(record):
            line_to_process = line.rstrip().split(',')
            if platename == line_to_process[0]:
                line_to_process.append(timestamp())
                line_updated = ','.join(line_to_process) + '\n'
                plate_in_file = True
                number_of_times_flagged = len(line_to_process) - 1
                break

        if plate_in_file:
            record[index_line] = line_updated
        else:
            record.append(platename + ',' + timestamp() + '\n')

        with open(record_file_path, 'w') as record_file:
            record_file.writelines( record )

    flagged_folder = '%s_%s' % (FLAG_FOLDER_PREFIX, str(number_of_times_flagged))
    return flagged_folder

def timestamp():
    return time.strftime('%Y-%m-%d %H:%M:%S')

def _adjust_output_if_fail_sanity_check(concentrations, blanks_col,
                                        good_cells, concentrations_minimum,
                                        concentration_maximum,
                                        regressed, r_minimum,
                                        output_folder, platename, mouse_id):
    pass_regression = _sanity_check_regression(regressed, r_minimum)
    pass_blanks = _sanity_check_blanks(concentrations, blanks_col)
    pass_samples = _sanity_check_samples(good_cells, concentrations_minimum)
    pass_concentration = _sanity_check_concentration(concentrations,
                                                     concentration_maximum)

    checks = pass_regression, pass_blanks, pass_samples, pass_concentration

    if sum(checks) < len(checks):
        flag_folder = record_flagged_plate_and_determine_folder(output_folder, platename)
        return _append_flagged_output_folder(output_folder, flag_folder,
                                             'repeated flags', platename,
                                             mouse_id)

    #I don't think this actually ever gets used.
    # if not pass_regression:
    #     output_folder = _append_flagged_output_folder(output_folder,
    #                                                   '1stpass_regression',
    #                                                   'regression', platename,
    #                                                   mouse_id)
    # elif not pass_blanks:
    #     output_folder = _append_flagged_output_folder(output_folder,
    #                                                   '2ndpass_blanks',
    #                                                   'blanks', platename,
    #                                                   mouse_id)
    # elif not pass_samples:
    #     output_folder = _append_flagged_output_folder(output_folder,
    #                                                   '3rdpass_samples',
    #                                                   'samples', platename,
    #                                                   mouse_id)
    # elif not pass_concentration:
    #     output_folder = _append_flagged_output_folder(output_folder,
    #                                                   '4thpass_concentration',
    #                                                   'concentration too high',
    #                                                   platename,
    #                                                   mouse_id)
    return output_folder


def _append_flagged_output_folder(output_folder, flagname, reason, platename,
                                  mouse_id):
    output_folder = os.path.join(output_folder, FLAGGED, flagname)
    print(f'\t{platename} ({mouse_id}) was flagged for {reason}')
    return output_folder


def _sanity_check_concentration(concentrations, concentration_maximum):
    """Returns True if sanity checked passed"""
    return np.all(concentrations <= concentration_maximum)


def _sanity_check_regression(regressed, r_minimum):
    """Returns True if sanity checked passed"""
    pass_sanity_check = regressed.rvalue >= r_minimum
    return pass_sanity_check


def _sanity_check_blanks(concentrations, blanks_col):
    """Make sure all concentrations in blanks columns are positive

    Returns
    -------
    True if sanity check passed
    """
    return concentrations[blanks_col].mean() > 0


def _sanity_check_standards(concentrations, standards, standards_col):
    """Ensure that standards correspond to increasing concentrations

    Check if wells with larger known concentrations have smaller measured
    concentrations than wells with smaller known concentrations. E.g. if the 0
    .5 concentrations wells were measured as smaller than the 0.25
    concentrations wells.

    Returns
    -------
    True if sanity check passed

    """
    standards_unique = standards.sort_values().unique()
    second_smallest = concentrations.loc[standards == standards_unique[1],
                                         standards_col]
    third_smallest = concentrations.loc[standards == standards_unique[2],
                                        standards_col]
    pass_sanity_check = third_smallest.map(
        lambda x: ((second_smallest - x) < 0).any()).any()
    return pass_sanity_check


def _sanity_check_samples(good_cells, threshold=CONCENTRATIONS_MINIMUM):
    """Make sure the mean concentrations of the good cells is above 0.7

    Returns
    -------
    True if sanity check passed
    """
    mean = np.mean(good_cells.values[pd.notnull(good_cells)])
    std = np.std(good_cells.values[pd.notnull(good_cells)])
    pass_sanity_check = mean + std > threshold
    return pass_sanity_check


def _get_good_cells(concentrations, blanks_col, plate_name, mouse_id,
                    plot=True, output_folder='.'):
    """Use blanks column to determine whether a well has enough fluorescence"""

    average_blanks = concentrations[blanks_col].mean()
    std_blanks = concentrations[blanks_col].std()

    # Minimum threshold: One standard deviation away from the mean
    avg_std = average_blanks + std_blanks

    is_cell_good = concentrations > avg_std

    n_good_cells = is_cell_good.sum().sum()
    # print(
    #     f'{plate_name} ({mouse_id}) has {n_good_cells} cells passing C'
    #     f'oncentration QC')
    good_cells = concentrations[is_cell_good]

    without_standards_or_blanks = good_cells.loc[:, :(blanks_col - 1)]
    if plot:
        _heatmap(without_standards_or_blanks, plate_name,
                 'concentrations_cherrypicked_no_standards_or_blanks',
                 output_folder)

    #this is where I should also return the concentrations minus the blank
    return without_standards_or_blanks


def _make_pick_list_filename(output_folder, datatype, plate_name):
    csv = os.path.join(output_folder, datatype, f'{plate_name}_echo.csv')
    maybe_make_directory(csv)
    return csv


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
    filename = _make_pick_list_filename(output_folder, datatype, plate_name)
    echo_picks.to_csv(filename, index=False)
    print(f'Wrote {datatype} ECHO pick list to {filename}')


def subtract_blank_concentration(concentrations, blanks_col):
    average_blanks = concentrations[blanks_col].mean()
    con_minus_blank = concentrations - average_blanks
    without_standards_or_blanks = con_minus_blank.loc[:, :(blanks_col - 1)]
    return without_standards_or_blanks

@click.command(short_help="Use 384-well plate reader fluorescence to choose "
                          "only cells with high enough signals")
@click.argument('filename', nargs=1,
                type=click.Path(dir_okay=False, readable=True, file_okay=True))
@click.argument('plate_name')
@click.argument('mouse_id')
@click.option('--filetype', default='txt')
@click.option('--standards-col', default=STANDARDS_COL, type=int,
              help='Column containing concentration standards. used for linear'
                   ' regression.')
@click.option('--blanks-col', default=BLANKS_COL,
              help='Column number containing blanks aka empty wells')
@click.option('--standards', default=STANDARDS_STR,
              help='Values of the ')
@click.option('--plot', is_flag=True)
@click.option('--output-folder', default='.')
@click.option('--inner-standards', default=True, type=bool)
@click.option('--concentrations-minimum', default=CONCENTRATIONS_MINIMUM,
              help='Minimum value (in ug/ml) of concentrations for '
                   '(mean + std) of cherrypicked cells')
@click.option('--concentrations-maximum', default=CONCENTRATIONS_MAXIMUM,
              help='Minimum value (in ug/ml) of global concentrations for a '
                   'plate. If any cell in a plate is above this value, the '
                   'plate is flagged')
@click.option('--r-minimum', default=R_MINIMUM,
              help='Minimum value of pearson correlation between regression '
                   'and standards lines')
@click.option('--subtract-blank-concentration-csv', default=False, type=bool,
              help='This option will generate a csv with the concentration of every cell minus the concentration of the average blanks')
def cherrypick(filename, plate_name, mouse_id, subtract_blank_concentration_csv, filetype='txt',
               standards_col=STANDARDS_COL, blanks_col=BLANKS_COL,
               standards=STANDARDS_STR,
               plot=True, output_folder='.',
               inner_standards=True,
               concentrations_minimum=CONCENTRATIONS_MINIMUM,
               concentrations_maximum=CONCENTRATIONS_MAXIMUM,
               r_minimum=R_MINIMUM):
    """Transform plate of cDNA fluorescence to ECHO pick list

    \b
    Parameters
    ----------
    filename : str
        Name of the cDNA fluorescence 384 well QC output
    plate_name : str
        Name of the plate
    mouse_id : str
        Name of the mouse, necessary for creating the cherrypick/non cherrypick
        lists

    Returns
    -------

    """

    main(filename, plate_name, mouse_id, subtract_blank_concentration_csv, output_folder=output_folder, plot=True)


def main(filename,
         plate_name,
         mouse_id,
         subtract_blank_concentration_csv,
         filetype='txt',
         standards_col=STANDARDS_COL,
         blanks_col=BLANKS_COL,
         standards=STANDARDS_STR,
         plot=True,
         output_folder='.',
         inner_standards=True,
         concentrations_minimum=CONCENTRATIONS_MINIMUM,
         concentrations_maximum=CONCENTRATIONS_MAXIMUM,
         r_minimum=R_MINIMUM):

    standards = _parse_standards(standards)
    # plate_name = filename_to_plate_name(filename)
    # mouse_id = plate_name_to_mouse_id(plate_name)
    fluorescence = _parse_fluorescence(filename, filetype)

    concentrations, means, regressed = _fluorescence_to_concentration(
        fluorescence, standards_col, standards, output_folder=output_folder,
        inner=inner_standards, r_minimum=r_minimum)

    good_cells = _get_good_cells(concentrations, blanks_col, plate_name,
                                 mouse_id, output_folder=output_folder,
                                 plot=plot)

    output_folder = _adjust_output_if_fail_sanity_check(
        concentrations, blanks_col, good_cells,
        concentrations_minimum, concentrations_maximum,
        regressed, r_minimum, output_folder, plate_name, mouse_id)

    if subtract_blank_concentration_csv:
        print("Option provided to subtract blank concentration from main concentration")
        cons_minus_blanks = subtract_blank_concentration(concentrations, blanks_col)
        _transform_to_pick_list(cons_minus_blanks, plate_name, mouse_id,
                                'minus_blanks', output_folder=output_folder)

    picklist_csv = _make_pick_list_filename(output_folder, 'cherrypicked',
                                            plate_name)


    if os.path.exists(picklist_csv):
        print(f'\t{plate_name} already cherrypicked, skipping ...')
        return

    if plot:
        _plot_regression(means, regressed, plate_name,
                         output_folder=output_folder)

        _heatmap(fluorescence / 1e6, plate_name, 'fluorescence', output_folder,
                 fmt='.1f', title_suffix=' (in 100,000 fluorescence units)')
        _heatmap(concentrations, plate_name, 'concentrations', output_folder,
                 fmt='.1f', vmin=0, vmax=1)


    _transform_to_pick_list(good_cells, plate_name, mouse_id, 'cherrypicked',
                            output_folder=output_folder)
    _transform_to_pick_list(concentrations, plate_name, mouse_id,
                            'non_cherrypicked', output_folder=output_folder)
