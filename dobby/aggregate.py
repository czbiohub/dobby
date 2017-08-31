import os
import warnings

with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    import pandas as pd

import click

PLATE_SIZE = 384


@click.command(short_help="Collect cherrypicked files into 384-well ECHO pick "
                          "list ready files")
@click.argument('filenames', nargs=-1, type=click.Path(dir_okay=False,
                                                       readable=True))
@click.option('--plate-size', type=int, default=PLATE_SIZE)
@click.option('--output-folder', default='.', type=click.Path(dir_okay=True,
                                                              writable=True))
def aggregate(filenames, plate_size, output_folder):
    aggregated = pd.DataFrame()
    seen = []
    i = 0

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for filename in filenames:
        seen.append(filename)
        df = pd.read_csv(filename)
        end_row = plate_size-aggregated.shape[0]
        to_add = df.iloc[:end_row]
        to_keep = df.iloc[(end_row+1):]
        aggregated = pd.concat([aggregated, to_add])

        if aggregated.shape[0] == plate_size:
            basename = 'echo_picklist_{}.csv'.format(str(i).zfill(5))
            csv = os.path.join(output_folder, basename)
            aggregated.to_csv(csv)

            click.echo('Wrote {n} files ({names}) to {csv}'.format(
                n=len(seen), names=', '.join(seen), csv=csv))

            # Increment the sheet number
            i += 1
            
            # Reset the filename keepers and growing datafarame
            seen = []
            aggregated = to_keep

    if aggregated.shape[0] > 0:
        click.echo("({n}) files ({names}) didn't make it into a pick list "
                   ":(".format(n=len(seen), names=', '.join(seen)))


