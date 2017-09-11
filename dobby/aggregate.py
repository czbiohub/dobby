import glob
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
PICKLIST_PREFIX = 'echo_picklist_'

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


def _picklist_basename(picklist_number):
    """Create picklist filename from the number sheet we're on"""
    n = str(picklist_number).zfill(5)
    return f'{PICKLIST_PREFIX}{n}.csv'


def _read_existing_picklists(folder):
    """Aggregate existing picklists into a 'database'"""
    dfs = []
    done_picklists = glob.iglob(os.path.join(folder,
                                             PICKLIST_PREFIX + "*.csv"))
    for filename in done_picklists:
        df = pd.read_csv(filename)
        basename = os.path.basename(filename)
        prefix, extension = basename.split('.')
        *prefix, number = prefix.split('_')
        number = int(number)
        df['number'] = number
        dfs.append(df)

    picklisted = pd.concat(dfs)
    return picklisted


@click.command(short_help="Collect cherrypicked files into 384-well ECHO pick "
                          "list ready files")
@click.argument('filenames', nargs=-1,
                type=click.Path(dir_okay=False, readable=True))
@click.option('--plate-size', type=int, default=PLATE_SIZE,
              help='Number of samples in the final plate')
@click.option('--output-folder', default='.',
              help="Folder to output the aggregated files to",
              type=click.Path(dir_okay=True, writable=True))
@click.option('--desired-concentration', default=0.5, type=float,
              help='Concentration in ng/ul')
@click.option('--final-volume', default=400, type=int,
              help='Volume to dilute cDNA to')
@click.option('--round-volume-to', default=ROUND_VOLUME_TO,
              help="Many machines can't produce volumes of any precision, so "
                   "this ensures that the final volumes are rounded to a "
                   "usable number")
@click.option('--force', is_flag=True,
              help="If specified, overwrite existing picklists")
def aggregate(filenames, plate_size, output_folder, desired_concentration=0.5,
              final_volume=400, round_volume_to=ROUND_VOLUME_TO, force=False):
    """Glue together cherrypick files by 384 samples for an ECHO pick list
    
    \b
    Parameters
    ----------
    filenames : str
        Tidy files created by "dobby cherrypick" to aggregate 
    """
    click.echo(f'Reading exising pick lists in {output_folder} ...')


    picklisted = None
    picklist_number = 0
    picked_plates = set([])

    try:
        picklisted = _read_existing_picklists(output_folder)
        picklist_number = picklisted['number'].max()
        picked_plates = set(picklisted['Plate number'].unique())
    except ValueError:
        # No objects to concatenate -- no picklist files in the output folder
        pass

    click.echo(f'\tDone. {picklist_number} picklists found.')

    if force:
        picklisted = None
        picklist_number = 0
        picked_plates = set([])
        click.echo(f'--force set: Overwriting existing {picklist_number} '
                   f'picklists.')

    mass = desired_concentration * final_volume

    aggregated = pd.DataFrame()
    seen = []

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for filename in filenames:
        platename = os.path.basename(filename).split('.')[0].split()[0].split('_')[0]

        samples = []
        if picklisted is not None and platename in picked_plates:
            rows = picklisted['Plate number'] == platename
            plate_picklist = picklisted.loc[rows]
            plate_list_numbers = plate_picklist['number'].unique()
            plate_list_number_max = plate_list_numbers.max()
            samples = plate_picklist['Combined name']

            picklist_basenames = ','.join(map(_picklist_basename,
                                              plate_list_numbers))

            # Remove sequential -1-1 and make sure only one -1 is left
            samples = [x.rstrip('-1') + '-1' for x in samples]

            if plate_list_number_max < picklist_number:
                click.echo(f'Already saw {platename} in '
                           f'{picklist_basenames}, skipping ...')
                continue

        seen.append(os.path.basename(filename))
        df = pd.read_csv(filename)
        df = df.sort_values(['row_letter', 'column_number'])
        # If this plate was in the very last picklist, see if any samples are
        # left over and need to be put into the next picklist
        if samples:
            remaining_rows = ~df['name'].isin(samples)
            n_remaining = remaining_rows.sum()
            n_samples = len(samples)
            click.echo(f'\tAlready wrote {n_samples} samples to '
                       f'{picklist_basenames}, {n_remaining} samples remaining'
                       f' for next picklist')
            df = df.loc[remaining_rows]

        end_row = plate_size-aggregated.shape[0]
        to_add = df.iloc[:end_row]
        to_keep = df.iloc[(end_row+1):]
        aggregated = pd.concat([aggregated, to_add])

        if aggregated.shape[0] == plate_size:
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

            aggregated['Destination well'] = DESTINATIONS

            # Reorder the columns
            aggregated = aggregated[COLUMNS]

            picklist_basename = _picklist_basename(picklist_number)
            csv = os.path.join(output_folder, picklist_basename)
            aggregated.to_csv(csv, index=False)

            click.echo('Wrote {n} files ({names}) to {csv}'.format(
                n=len(seen), names=', '.join(seen), csv=csv))

            # Increment the sheet number
            picklist_number += 1

            # Reset the filename keepers and growing datafarame
            seen = [filename]
            aggregated = to_keep

    if aggregated.shape[0] > 0:
        click.echo("{n} samples from ({names}) didn't make it into a pick "
                   "list "
                   ":(".format(n=aggregated.shape[0], names=', '.join(seen)))


