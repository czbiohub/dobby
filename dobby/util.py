import os


def maybe_make_directory(filename):
    directory = os.path.dirname(filename)
    try:
        os.makedirs(directory)
    except FileExistsError:
        pass