import unittest
from dobby import cherrypick
from click.testing import CliRunner
import os
import shutil

parent_dir = os.path.split(os.path.dirname(cherrypick.__file__))[0]
cherrypick_test_dir = 'test/data/cherrypick'
BAD_PLATE = os.path.join(parent_dir, cherrypick_test_dir, 'input/bad_plate.txt')
BAD_PLATE_ONE = os.path.join(parent_dir, cherrypick_test_dir, 'input/bad_plate_MAA000321.txt')
BAD_PLATE_TWO = os.path.join(parent_dir, cherrypick_test_dir, 'input/bad_plate_MAA000344.txt')
GOOD_PLATE = os.path.join(parent_dir, cherrypick_test_dir, 'input/good_plate.txt')
OUTPUT_FOLDER = os.path.join(parent_dir, cherrypick_test_dir, 'output')


class TestCherrypick(unittest.TestCase):
    def file_len(self,fname):
        with open(fname) as f:
            for i, l in enumerate(f):
                pass
        return i + 1

    def test_goodplate_rightoutput(self):
        output_folder = os.path.join(OUTPUT_FOLDER, 'test_goodplate_rightoutput')
        if os.path.exists(output_folder):
            shutil.rmtree(output_folder)
        cherrypick.main(GOOD_PLATE, 'good_plate', 'my_mouse_id', output_folder=output_folder)

        assert os.path.exists(os.path.join(output_folder, 'concentrations'))
        assert os.path.exists(os.path.join(output_folder, 'cherrypicked'))
        assert os.path.exists(os.path.join(output_folder, 'fluorescence'))
        assert os.path.exists(os.path.join(output_folder, 'non_cherrypicked'))
        assert os.path.exists(os.path.join(output_folder, 'regression'))

        shutil.rmtree(output_folder)

    def test_1_flagged(self):
        dir_1_flagged = cherrypick.FLAG_FOLDER_PREFIX + '_' + '1'
        output_folder = os.path.join(OUTPUT_FOLDER, '1_flagged_test_output')
        cherrypick.main(BAD_PLATE, 'bad_plate', 'bad_mouse_id', output_folder=output_folder)

        assert os.path.exists(os.path.join(output_folder, cherrypick.FLAGGED, dir_1_flagged,'cherrypicked'))
        assert os.path.exists(os.path.join(output_folder, cherrypick.FLAGGED, dir_1_flagged,'concentrations'))
        assert os.path.exists(os.path.join(output_folder, cherrypick.FLAGGED, dir_1_flagged,'fluorescence'))
        assert os.path.exists(os.path.join(output_folder, cherrypick.FLAGGED, dir_1_flagged,'non_cherrypicked'))
        assert os.path.exists(os.path.join(output_folder, cherrypick.FLAGGED, dir_1_flagged,'regression'))
        assert os.path.exists(os.path.join(output_folder, cherrypick.FLAGGED, cherrypick.RECORD_FILE) )

        shutil.rmtree(output_folder)

    def test_multiple_files_flagged(self):
        dir_1_flagged = cherrypick.FLAG_FOLDER_PREFIX + '_' + '1'
        output_folder = os.path.join(OUTPUT_FOLDER, 'multiple_files_flagged_test_output')
        cherrypick.main(BAD_PLATE_ONE, 'MAA000321', 'bad_mouse_id', output_folder=output_folder)
        cherrypick.main(BAD_PLATE_ONE, 'MAA000344', 'bad_mouse_id', output_folder=output_folder)
        cherrypick.main(BAD_PLATE, 'bad_plate', 'bad_mouse_id', output_folder=output_folder)

        assert os.path.exists(os.path.join(output_folder, cherrypick.FLAGGED, dir_1_flagged,'cherrypicked'))
        assert os.path.exists(os.path.join(output_folder, cherrypick.FLAGGED, dir_1_flagged,'concentrations'))
        assert os.path.exists(os.path.join(output_folder, cherrypick.FLAGGED, dir_1_flagged,'fluorescence'))
        assert os.path.exists(os.path.join(output_folder, cherrypick.FLAGGED, dir_1_flagged,'non_cherrypicked'))
        assert os.path.exists(os.path.join(output_folder, cherrypick.FLAGGED, dir_1_flagged,'regression'))
        record_file_path = os.path.join(output_folder, cherrypick.FLAGGED, cherrypick.RECORD_FILE)
        assert os.path.exists( record_file_path )

        assert self.file_len(record_file_path) == 3

        shutil.rmtree(output_folder)

    def test_2_flagged(self):
        output_folder = os.path.join(OUTPUT_FOLDER, '2_flagged_test_output')
        record_file_dir = os.path.join(output_folder, cherrypick.FLAGGED)
        record_file_path = os.path.join(record_file_dir, cherrypick.RECORD_FILE)
        platename = 'bad_plate'
        if not os.path.exists(record_file_path):
            if not os.path.exists(record_file_dir):
                os.makedirs(record_file_dir)

            with open(record_file_path, 'w') as record_file:
                record_file.write('bad_plate' + ',' + '2017-09-21 18:44:44' + '\n')

        cherrypick.main(BAD_PLATE, 'bad_plate', 'bad_mouse_id', output_folder=output_folder)

        dir_2_flagged = cherrypick.FLAG_FOLDER_PREFIX + '_' + '2'

        assert os.path.exists(os.path.join(output_folder, cherrypick.FLAGGED, dir_2_flagged,'cherrypicked'))
        assert os.path.exists(os.path.join(output_folder, cherrypick.FLAGGED, dir_2_flagged,'concentrations'))
        assert os.path.exists(os.path.join(output_folder, cherrypick.FLAGGED, dir_2_flagged,'fluorescence'))
        assert os.path.exists(os.path.join(output_folder, cherrypick.FLAGGED, dir_2_flagged,'non_cherrypicked'))
        assert os.path.exists(os.path.join(output_folder, cherrypick.FLAGGED, dir_2_flagged,'regression'))
        assert os.path.exists(os.path.join(output_folder, cherrypick.FLAGGED, cherrypick.RECORD_FILE) )
        shutil.rmtree(output_folder)

    def test_3_flagged(self):
        pass

    def test_1_failed_then_pass(self):
        pass

    def test_2_failed_then_pass(self):
        pass

    def create_record(self):
        output_folder = os.path.join(OUTPUT_FOLDER, 'create_record_output')
        folder = cherrypick.record_flagged_plate_and_determine_folder(output_folder, 'my_plate')
        assert folder == 'flag_1'
        shutil.rmtree(output_folder)
        #source of truth file for number of times a plate has been flagged
if __name__ == '__main__':
    unittest.main()
