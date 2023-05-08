import unittest
from unittest.mock import patch
import os
import sys
import pandas as pd
from mongoengine import connect
dir_path = os.path.dirname(os.path.realpath(__file__))
project_dir_path = os.path.abspath(os.path.join(dir_path, '..'))
sys.path.append(project_dir_path)
from io import StringIO
import config as c

from Scripts.import_crop import import_crops, import_groups, read_file

class TestImportCountries(unittest.TestCase):
    
    def setUp(self):
        # Create a temporary crops.csv file
        self.df_crop = pd.DataFrame({'ext_id': [1, 2],
            'name': ['african_maize', 'banana'],
            'base_name': ['maize', 'banana'],
            'app_name': ['Maize (Africa)', 'Banana']})

        self.df_group = pd.DataFrame({'crop': [1, 1, 1, 1, 2],
            'ext_id': ['1_1', '1_2', '1_3', '1_4', '2_1'],
            'group_name': ['g1', 'g2', 'g3', 'g4', 'Musa']})
        # Create a connection database test
        connect('test_gap_analysis', host='mongomock://localhost', uuidRepresentation='standard')
        
    def test_read_crop_file(self):
        # Test with a DataFrame
        df = read_file(df = self.df_crop, columns = c.cols_crop)
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(len(df), 2)

        # Test with a file that doesn't exist
        df = read_file()
        self.assertIsNone(df)

        # Test with a file that the required columns don't exist
        df_error_crop = pd.DataFrame({'ext_Id': [1, 2],
            'name': ['african_maize', 'banana'],
            'base_name': ['maize', 'banana'],
            'app_name': ['Maize (Africa)', 'Banana']})
        
        with self.assertRaisesRegex(ValueError, "Missing required columns in crops.csv file: ext_id"):
            read_file(df_error_crop, 'crops.csv', c.cols_crop)

    def test_read_group_file(self):
        # Test with a DataFrame
        df = read_file(df = self.df_group, columns = c.cols_group)
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(len(df), 5)

        # Test with a file that doesn't exist
        df = read_file()
        self.assertIsNone(df)

        # Test with a file that the required columns don't exist
        df_error_group = pd.DataFrame({'Crop': [1, 1, 1, 1, 2],
            'ext_id': ['1_1', '1_2', '1_3', '1_4', '2_1'],
            'group_name': ['g1', 'g2', 'g3', 'g4', 'Musa']})
        
        with self.assertRaisesRegex(ValueError, "Missing required columns in groups.csv file: crop"):
            read_file(df_error_group, 'groups.csv', c.cols_group)

    def test_import_crops(self):
        #self.df_crop.to_csv(os.path.join(project_dir_path, 'Inputs','crops.csv'))
        with StringIO() as output:
            sys.stdout = output

            # Call the function you want to test
            import_crops(self.df_crop)

            # Get the output and reset stdout
            out = output.getvalue()
            sys.stdout = sys.__stdout__

            # Check that the output is correct
            self.assertIn('Processed 2 rows.', out)
            self.assertIn('Successfully saved 2 rows.', out)
            self.assertIn('No errors found', out)

        #Test import crops error
        with StringIO() as output:
            sys.stdout = output
            import_crops(self.df_crop)

            # Get the output and reset stdout
            out = output.getvalue()
            sys.stdout = sys.__stdout__

            # Check that the output is correct
            self.assertIn('Processed 2 rows.', out)
            self.assertIn('Successfully saved 0 rows.', out)
            self.assertIn('Failed to save 2 rows.', out)

            self.assertTrue(os.path.isfile(os.path.join(project_dir_path, 'Outputs/crop_logs.xlsx')))


    def test_import_groups(self):
        #self.df_group.to_csv(os.path.join(project_dir_path, 'Inputs','groups.csv'))
        with StringIO() as output:
            sys.stdout = output

            # Call the function you want to test
            import_groups(self.df_group)

            # Get the output and reset stdout
            out = output.getvalue()
            sys.stdout = sys.__stdout__

            # Check that the output is correct
            self.assertIn('Processed 5 rows.', out)
            self.assertIn('Successfully saved 5 rows.', out)
            self.assertIn('No errors found', out)

        #Test import crops error
        with StringIO() as output:
            sys.stdout = output
            
            import_groups(self.df_group)

            # Get the output and reset stdout
            out = output.getvalue()
            sys.stdout = sys.__stdout__

            # Check that the output is correct
            self.assertIn('Processed 5 rows.', out)
            self.assertIn('Successfully saved 0 rows.', out)
            self.assertIn('Failed to save 5 rows.', out)

            self.assertTrue(os.path.isfile(os.path.join(project_dir_path, 'Outputs/group_logs.xlsx')))


if __name__ == '__main__':
    unittest.main()

