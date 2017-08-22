import os

import pytest

@pytest.fixture
def data_folder():
    dirname = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(dirname, 'data')


@pytest.fixture
def raw_fluorescence(data_folder):
    return os.path.join(data_folder, 'MAA000154.txt')


@pytest.fixture
def fluorescence(data_folder):
    return os.path.join(data_folder, 'MAA000154.csv')


@pytest.fixture
def concentration(data_folder):
    return os.path.join(data_folder, 'concentration', 'MAA000154.csv')