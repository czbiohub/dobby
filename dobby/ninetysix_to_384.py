import pandas as pd


def get_384_column_number(ninety_six_column_number, verbose=False):
    """Convert 96 well plate column number to destination 384 well plate col"""
    # This is operated on the whole mini-dataframe column number which
    # is by definition the same since we made mini-dataframes with groupby()
    # So we just need to extract the first one, aka the 0th index
    ninety_six_column_number = ninety_six_column_number.iloc[0]

    column_i = ninety_six_column_number * 2 - 1
    new_column_numbers = list(range(column_i, column_ i + 2))
    reordered_column_numbers = new_column_numbers + new_column_numbers
    if verbose:
        print(
        f"converted: {ninety_six_column_number} --> " \
         "{reordered_column_numbers}")
        return pd.Series(reordered_column_numbers)


def get_384_row_letter(ninety_six_row_letter, verbose=False):
    """Convert 96 well plate row letter to destination 384 well plate row"""
    # This is operated on the whole mini-dataframe row number which
    # is by definition the same since we made mini-dataframes with groupby()
    # So we just need to extract the first one, aka the 0th index
    ninety_six_row_letter = ninety_six_row_letter.iloc[0]
    row_i = string.ascii_uppercase.index(ninety_six_row_letter)

    new_row_letters = string.ascii_uppercase[row_i * 2:(row_i * 2 + 2)]
    reordered_row_letters = [new_row_letters[int(i / 2)] for i in range(4)]
    if verbose:
        print(f"converted: {ninety_six_row_letter} --> " \
               "{reordered_row_letters}")
        return pd.Series(reordered_row_letters)


def 


@click.command(short_help="Collect cherrypicked files into 384-well ECHO pick "
                          "list ready files")
@click.argument('ninetysix_plates', nargs=-1,
                type=click.Path(dir_okay=False, readable=True))
def ninteysix_to_384(ninetysix_plates):
    """Converts 96 well plates into aggregated 384 well pones

    Parameters
    ----------
    ninetysix_plates : list
        csv filenames of 96-well plates to aggregate and convert to 384 well
        plates

    Returns
    -------
    Writes csv files of 384 well plates
    """

    for plate in ninetysix_plates:
