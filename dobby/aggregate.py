import os
import string
import warnings

with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    import pandas as pd

import click

PLATE_SIZE = 384

ROWS = string.ascii_uppercase[:16]
COLS = range(1, 25)

ROUND_VOLUME_TO = 0.5

DESTINATIONS = [f'{row}{col}' for row in ROWS for col in COLS]


COLUMNS = ['Source well',
 'Plate number',
 'Name',
 'C(ng/ul)',
 'Type',
 'Verdict',
 'Combined name',
 'Desired C',
 'Final V',
 'Sample V',
 'Buffer V',
 'Rounded Sample V',
 'Rounded Buffer V',
 'Destination well']


def round_partial(value, resolution):
    """Round to a fraction of a number, e.g. to closest 0.25

    From https://stackoverflow.com/a/8118808
    """
    return round(value/resolution) * resolution


@click.command(short_help="Collect cherrypicked files into 384-well ECHO pick "
                          "list ready files")
@click.argument('filenames', nargs=-1,
                type=click.Path(dir_okay=False, readable=True))
@click.option('--plate-size', type=int, default=PLATE_SIZE,
              help='Number of samples in the final plate')
@click.option('--output-folder', default='.',
              help="Folder to output the aggregated files to",
              type=click.Path(dir_okay=True, writable=True))
@click.option('--desired-concentration', default=0.3, type=float,
              help='Concentration in ng/ul')
@click.option('--final-volume', default=400, type=int,
              help='Volume to dilute cDNA to')
@click.option('--round-volume-to', default=ROUND_VOLUME_TO,
              help="Many machines can't produce volumes of any precision, so "
                   "this ensures that the final volumes are rounded to a "
                   "usable number")
def aggregate(filenames, plate_size, output_folder, desired_concentration,
              final_volume=400, round_volume_to=ROUND_VOLUME_TO):
    """Glue together cherrypick files by 384 samples for an ECHO pick list

    \b
    Parameters
    ----------
    filenames : str
        Tidy files created by "dobby cherrypick" to aggregate
    """
    aggregated = pd.DataFrame()
    sheet_number = 0

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    last_file = len(filenames) - 1

    for file_index, filename in enumerate(filenames):
        df = pd.read_csv(filename)
        df = df.sort_values(['row_letter', 'column_number'])

        rows_filled = aggregated.shape[0]
        end_row_index = plate_size - rows_filled
        add_now = df.iloc[:end_row_index]
        add_next_time = df.iloc[(end_row_index):] # this +1 should not be here
        aggregated = pd.concat([aggregated, add_now])

        is_last_file = file_index == last_file
        is_complete_platesize = aggregated.shape[0] == plate_size
        # end_on_incomplete_sheet = (file_index == last_file and add_next_time.shape[0] != 0)
        if is_complete_platesize or is_last_file:
            is_partial_sheet = (is_last_file and not is_complete_platesize)
            formatted_echopick_sheet = format_for_echopick(
                aggregated,
                desired_concentration,
                final_volume,
                round_volume_to,
                is_partial_sheet)

            write_csv_from_dataframe(formatted_echopick_sheet, sheet_number, output_folder, is_partial_sheet)
            # Increment the sheet number
            sheet_number += 1

            # Reset the filename keepers and growing datafarame
            aggregated = add_next_time

            rows_leftover_from_lastfile = add_next_time.shape[0]
            if is_last_file and rows_leftover_from_lastfile > 0:
                formatted_echopick_sheet = format_for_echopick(
                    aggregated,
                    desired_concentration,
                    final_volume,
                    round_volume_to,
                    True)

                write_csv_from_dataframe(formatted_echopick_sheet, sheet_number, output_folder, True)


def write_csv_from_dataframe(dataframe, sheet_number, output_folder, is_partial_sheet=False):
    #generate_file
    basename = 'echo_picklist_{}.csv'.format(str(sheet_number).zfill(5))
    if is_partial_sheet:
        basename = 'echo_picklist_{}_incomplete.csv'.format(str(sheet_number).zfill(5))
    csv = os.path.join(output_folder, basename)
    dataframe.to_csv(csv, index=False)


def format_for_echopick(aggregated,desired_concentration,final_volume,round_volume_to,is_partial_sheet=False):
    mass = desired_concentration * final_volume
    aggregated = aggregated.rename(
     columns={"well": "Source well", 'concentration': 'C(ng/ul)',
              'plate': 'Plate number', 'name': "Name", })
    aggregated['Desired C'] = desired_concentration
    aggregated['Final V'] = final_volume
    aggregated["Verdict"] = 1
    aggregated['Type'] = 'Unknown'

    aggregated['Combined name'] = aggregated['Name'] + '-' \
                               + aggregated['Verdict'].astype(str)

    # In case the sample volume is bigger than the final volume, take
    # the minimum
    aggregated['Sample V'] = aggregated['C(ng/ul)'].map(
     lambda x: min(mass/x, final_volume))
    aggregated['Buffer V'] = final_volume - aggregated['Sample V']

    aggregated['Rounded Sample V'] = aggregated['Sample V'].map(
     lambda x: round_partial(x, round_volume_to))
    aggregated['Rounded Buffer V'] = final_volume - \
                                  aggregated['Rounded Sample V']

    well_names = DESTINATIONS
    if is_partial_sheet: #TODO
        last_index = len(aggregated['Rounded Buffer V'])
        well_names = DESTINATIONS[:last_index]

    aggregated['Destination well'] = well_names

    # Reorder the columns
    aggregated = aggregated[COLUMNS]

    return aggregated
