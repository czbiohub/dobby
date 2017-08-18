import os

from scipy.stats import linregress
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

N_EXTRA_LINES = 409
COLUMNS_TO_PARSE = 'C:Z'
ROWS_TO_SKIP = 2

STANDARDS = pd.Series(
    [8, 8, 6, 6, 4, 4, 2, 2, 1, 1, 0.5, 0.5, 0.025, 0.025, 0, 0])
STANDARDS_COL = 24
BLANKS_COL = 23


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
    return parser(filename, **kwargs)


def _maybe_make_directory(filename):
    directory = os.path.dirname(filename)
    try:
        os.mkdir(directory)
    except FileExistsError:
        pass


def _plot_regression(means, regressed, plate_name, output_folder='.'):
    means.plot(legend=True)
    y = pd.Series(regressed.slope * means.index + regressed.intercept,
                  index=means.index,
                  name='Regression')
    y.plot(legend=True)

    # :.5 indicates 5 decimal places
    plt.title(f'$R^2$ = {regressed.rvalue:.5}')

    pdf = os.path.join(output_folder, 'regression',
                       f'{plate_name}_regression_lines.pdf')
    _maybe_make_directory(pdf)
    plt.savefig(pdf)
    return pdf


def _heatmap(data, plate_name, datatype, output_folder):
    sns.heatmap(data)
    plt.title(f'{plate_name} {datatype}')
    pdf = os.path.join(output_folder, datatype,
                       f'{plate_name}_{datatype}_heatmap.pdf')
    _maybe_make_directory(pdf)
    plt.savefig(pdf)
    print(f'{plate_name}: Wrote {datatype} heatmap to {pdf}')
    return pdf


def _fluorescence_to_concentration(fluorescence, standards_col, standards,
                                   plate_name, plot=True,
                                   output_folder='.', r_minimum=0.98, ):
    """Use standards column to regress and convert to concentrations"""
    means = fluorescence[standards_col].groupby(standards).mean()
    stds = fluorescence[standards_col].groupby(standards).std()
    regressed = linregress(means.index, means)

    if (regressed.rvalue < r_minimum):
        raise ValueError(
            f'Regression failed test: {regressed.rvalue} < {r_minimum}')

    # Convert fluorescence to concentration
    concentrations = (fluorescence - regressed.intercept) / regressed.slope

    if plot:
        pdf = _plot_regression(means, regressed, plate_name)
        print(f'{plate_name}: Wrote regression plot to {pdf}')

        _heatmap(fluorescence, plate_name, 'fluorescence', output_folder)
        _heatmap(concentrations, plate_name, 'concentrations', output_folder)

    return concentrations


def _get_good_cells(concentrations, blanks_col, plate_name, mouse_id,
                    plot=True,
                    output_folder='.'):
    """Use the blanks column to determine whether a well has enough fluorescence"""

    average_blanks = concentrations[blanks_col].mean()
    std_blanks = concentrations[blanks_col].std()

    # Minimum threshold: One standard deviation away from the mean
    avg_std = average_blanks + std_blanks

    is_cell_good = concentrations > avg_std
    n_good_cells = is_cell_good.sum().sum()
    print(
        f'{plate_name} ({mouse_id}) has {n_good_cells} cells passing Concentration QC')
    good_cells = concentrations[is_cell_good]

    without_standards_or_blanks = good_cells.loc[:, :(blanks_col - 1)]

    if plot:
        _heatmap(without_standards_or_blanks, plate_name,
                 'without_standards_or_blanks', output_folder)

    return without_standards_or_blanks


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
    _maybe_make_directory(csv)
    echo_picks.to_csv(csv, index=False)
    print(f'Wrote {datatype} ECHO pick list to {csv}')
    return csv


def make_echo_picks(filename, plate_name, mouse_id, filetype='excel',
                    standards_col=24, blanks_col=23, standards=STANDARDS,
                    plot=True,
                    output_folder='.'):
    fluorescence = _parse_fluorescence(filename, filetype)

    concentrations = _fluorescence_to_concentration(fluorescence,
                                                    standards_col,
                                                    standards, plate_name,
                                                    plot)
    good_cells = _get_good_cells(concentrations, blanks_col, plate_name,
                                 mouse_id,
                                 plot)

    _transform_to_pick_list(good_cells, plate_name, mouse_id, 'cherrypicked')
    _transform_to_pick_list(concentrations, plate_name, mouse_id,
                            'non_cherrypicked')