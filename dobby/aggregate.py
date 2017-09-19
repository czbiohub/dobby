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
@click.option('--incomplete-echopicklists-folder',
                type=click.Path(dir_okay=True, file_okay=False, readable=True))
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
def aggregate(filenames, incomplete_echopicklists_folder, output_folder, desired_concentration,
              final_volume=400, round_volume_to=ROUND_VOLUME_TO):
    """Glue together cherrypick files by 384 samples for an ECHO pick list

    \b
    Parameters
    ----------
    filenames : str
        Tidy files created by "dobby cherrypick" to aggregate
    """
    if not os.path.exists(output_folder):
        # dobby aggregate test/aggregate_input/* --output-folder test/aggregate_output/ --incomplete-echopicklists test/incomplete_input_aggregate/*
        os.makedirs(output_folder)

    plate_num = 0
    cherrypick_file_start = 0
    starting_dataframe = pd.DataFrame()
    left_over_dataframe = pd.DataFrame()

    if incomplete_echopicklists_folder:
        incomplete_echopiclist_files = file_rel_paths(incomplete_echopicklists_folder)

        incomplete_echopicklist_dataframes = dataframe_generator(incomplete_echopiclist_files)
        incomplete_echopicklist_dataframes_ofsize = dataframes_ofsize_generator(incomplete_echopicklist_dataframes, PLATE_SIZE)
        for echopicklist_dataframe_ofsize, is_lessthan_desired_size, files_used, left_over_dataframe in incomplete_echopicklist_dataframes_ofsize:
            if not is_lessthan_desired_size:
                write_csv_from_dataframe(echopicklist_dataframe_ofsize, plate_num, output_folder, is_lessthan_desired_size)
                plate_num +=1
                return # all concatenated incomplete echopicklists make

        # if there is an echopick list that is not the full size
        incomplete_echopicklist = echopicklist_dataframe_ofsize
        rows_to_complete = PLATE_SIZE - incomplete_echopicklist.shape[0]

        # complete incomplete echopicklist with cherrypicklists
        dataframes = dataframe_generator(filenames[cherrypick_file_start:], should_sort=True)
        dataframes_ofsize = dataframes_ofsize_generator(dataframes, rows_to_complete, starting_dataframe)
        dataframe, is_lessthan_desired_size, files_used, left_over_dataframe = next(dataframes_ofsize)
        is_lessthan_desired_size = True
        formatted_echopick_list = format_echopicklist(
            dataframe,
            desired_concentration,
            final_volume,
            round_volume_to,
            is_lessthan_desired_size)

        complete = pd.concat([incomplete_echopicklist, formatted_echopick_list])
        cherrypick_file_start = files_used
        #make csv file
        write_csv_from_dataframe(complete, plate_num, output_folder)
        #increment the plate_num
        plate_num +=1

        if files_used == len(filenames) and left_over_dataframe.shape[0] > 0:
            is_lessthan_desired_size = True
            formatted_echopick_list = format_echopicklist(
                left_over_dataframe,
                desired_concentration,
                final_volume,
                round_volume_to,
                is_lessthan_desired_size)

            #make csv file
            write_csv_from_dataframe(formatted_echopick_list, plate_num, output_folder, is_lessthan_desired_size)
            return


    dataframes = dataframe_generator(filenames[cherrypick_file_start:], should_sort=True)
    if not left_over_dataframe.empty:
        starting_dataframe = left_over_dataframe
    dataframes_ofsize = dataframes_ofsize_generator(dataframes, PLATE_SIZE, starting_dataframe)

    for dataframe, is_lessthan_desired_size, files_used, left_over_dataframe in dataframes_ofsize:
        formatted_echopick_list = format_echopicklist(
            dataframe,
            desired_concentration,
            final_volume,
            round_volume_to,
            is_lessthan_desired_size)

        write_csv_from_dataframe(formatted_echopick_list, plate_num, output_folder, is_lessthan_desired_size)
        # Increment the plate number
        plate_num += 1

def dataframe_generator(files, should_sort=False):
    for f in files:
        data_frame = pd.read_csv(f)
        if should_sort:
            yield data_frame.sort_values(['row_letter', 'column_number'])
        else:
            yield data_frame


def file_rel_paths(directory):
    rel_paths = []
    for f in os.listdir(directory):
        rel_paths.append(os.path.join(directory, f))
    return rel_paths


def dataframes_ofsize_generator(dataframes_generator, desired_size, starting_dataframe=None):
    dataframes_used = 0
    aggregated = pd.DataFrame()
    if starting_dataframe is not None:
        aggregated = starting_dataframe

    for dataframe in dataframes_generator:
        dataframes_used +=1
        rows_filled = aggregated.shape[0]
        end_row_index = desired_size - rows_filled
        add_now = dataframe.iloc[:end_row_index]
        add_next_time = dataframe.iloc[end_row_index:]
        aggregated = pd.concat([aggregated, add_now])
        is_complete_platesize = aggregated.shape[0] == desired_size
        if is_complete_platesize:
            is_lessthan_desired_size = not is_complete_platesize
            yield aggregated, is_lessthan_desired_size, dataframes_used, add_next_time

            aggregated = add_next_time

    if aggregated.shape[0] > 0:
        is_lessthan_desired_size = True
        yield aggregated, is_lessthan_desired_size, dataframes_used, add_next_time


def write_csv_from_dataframe(dataframe, plate_num, output_folder, is_incomplete_plate=False):
    #generate_file
    basename = 'echo_picklist_{}.csv'.format(str(plate_num).zfill(5))
    if is_incomplete_plate:
        basename = 'echo_picklist_{}_incomplete.csv'.format(str(plate_num).zfill(5))
    csv = os.path.join(output_folder, basename)
    dataframe.to_csv(csv, index=False)


def format_echopicklist(
        aggregated,
        desired_concentration,
        final_volume,
        round_volume_to,
        is_incomplete_plate=False):
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
    if is_incomplete_plate:
        last_index = len(aggregated['Rounded Buffer V'])
        well_names = DESTINATIONS[:last_index]

    aggregated['Destination well'] = well_names
    # Reorder the columns
    aggregated = aggregated[COLUMNS]

    return aggregated
