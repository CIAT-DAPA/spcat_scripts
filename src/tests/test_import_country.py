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

from Scripts.import_country import import_countries, read_countries_file

class TestImportCountries(unittest.TestCase):
    
    def setUp(self):
        # Create a temporary countries.csv file
        self.df = pd.DataFrame({
            'iso_2': ['AR', 'BR', 'CL'],
            'name': ['Argentina', 'Brazil', 'Chile']
        })
        # Create a connection database test
        connect('test_gap_analysis', host='mongomock://localhost', uuidRepresentation='standard')
        
    def test_read_countries_file(self):
        # Test with a DataFrame
        df = read_countries_file(self.df)
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(len(df), 3)

        # Test with a file that doesn't exist
        df = read_countries_file()
        self.assertIsNone(df)

        # Test with a file that the required columns don't exist
        df_error = pd.DataFrame({
            'Iso_2': ['AR', 'BR', 'CL'],
            'name': ['Argentina', 'Brazil', 'Chile']
        })
        
        with self.assertRaisesRegex(ValueError, "Missing required columns in countries.csv file: iso_2"):
            read_countries_file(df_error)
    
    def test_import_countries(self):
        #Test import countries success
        with StringIO() as output:
            sys.stdout = output
            import_countries(self.df)

            # Get the output and reset stdout
            out = output.getvalue()
            sys.stdout = sys.__stdout__

            # Check that the output is correct
            self.assertIn('Processed 3 rows.', out)
            self.assertIn('Successfully saved 3 rows.', out)
            self.assertIn('No errors found', out)

        #Test import countries error
        with StringIO() as output:
            sys.stdout = output
            import_countries(self.df)

            # Get the output and reset stdout
            out = output.getvalue()
            sys.stdout = sys.__stdout__

            # Check that the output is correct
            self.assertIn('Processed 3 rows.', out)
            self.assertIn('Successfully saved 0 rows.', out)
            self.assertIn('Failed to save 3 rows.', out)

            self.assertTrue(os.path.isfile(os.path.join(project_dir_path, 'Outputs/country_logs.xlsx')))


if __name__ == '__main__':
    unittest.main()

