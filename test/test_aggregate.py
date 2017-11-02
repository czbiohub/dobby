# SAMPLE RUN OF A SINGLE TEST: python -m unittest test_aggregate.TestAggregate.test_last_echopicklist_number
import unittest
from dobby import aggregate
from click.testing import CliRunner
import os
import shutil

parent_dir = os.path.split(os.path.dirname(aggregate.__file__))[0]
aggregate_test_dir = 'test/data/aggregate'
CHERRYPICK_PLATE = os.path.join(parent_dir, aggregate_test_dir, 'input/1.csv')
OUTPUT_FOLDER = os.path.join(parent_dir, aggregate_test_dir, 'output_folder')


class TestAggregate(unittest.TestCase):
    def file_len(self,fname):
        with open(fname) as f:
            for i, l in enumerate(f):
                pass
        return i + 1

    def test_last_echopicklist_number(self):
        output_folder = os.path.join(OUTPUT_FOLDER)

        largest_index = aggregate.largest_enumeration_in_outputfolder(OUTPUT_FOLDER)
        self.assertTrue(largest_index == int(2))

    #dobby aggregate test/data/aggregate/input/* --output-folder test/data/aggregate/output_folder
