import os

import pandas as pd


def maybe_make_directory(filename):
    directory = os.path.dirname(filename)
    try:
        os.makedirs(directory)
    except FileExistsError:
        pass


def _parse_standards(standards_str):
    return pd.Series(standards_str.split(',')).astype(float)


def filename_to_platename(filename):
    return os.path.splitext(os.path.basename(filename))[0]