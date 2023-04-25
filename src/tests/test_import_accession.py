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
from ormgap import Country, Crop, Group

from Scripts.import_accession import read_file, import_accessions, import_attributes

class TestImportCountries(unittest.TestCase):
    
    def setUp(self):
        # Create a temporary crops.csv file
        self.df_accessions = pd.DataFrame({
            'species_name': ['barley_growth_class', 'barley_growth_class', 'barley_growth_class', 'barley_growth_class', 'barley_growth_class'],
            'crop': [3, 3, 3, 3, 3],
            'landrace_group': ['3_1', '3_2', '3_2', '3_1', '3_1'],
            'country': ['GE', 'GE', 'TM', 'TM', 'TM'],
            'latitude': [41.45, 41.45, 37.95, 37.95, 37.2833],
            'longitude': [44.4667, 44.4667, 58.3667, 58.3667, 62.35],
            'ext_id': ['ICD_33_3', 'ICD_34_3', 'ICD_42_3', 'ICD_43_3', 'ICD_45_3'],
            'source_database': ['icarda', 'icarda', 'icarda', 'icarda', 'icarda'],
            'institution_name': ['ICARDA', 'ICARDA', 'ICARDA', 'ICARDA', 'ICARDA'],
            'accession_id': [16950, 16950, 16954, 16954, 16955]
        })

        self.df_attributes = pd.DataFrame({
            'key': ['height', 'drought tolerance', 'flowering time', 'height', 'drought tolerance', 'flowering time'],
            'value': ['170 cm', 'moderate', '140 days', '165 cm', 'high', '135 days'],
            'accession': ['ICD_33_3', 'ICD_33_3', 'ICD_33_3', 'ICD_34_3', 'ICD_34_3', 'ICD_34_3']
        })

        # Create a connection database test
        connect('test_gap_analysis', host='mongomock://localhost', uuidRepresentation='standard')
        
    def test_read_accession_file(self):

        # Test with a DataFrame
        df = read_file(df = self.df_accessions, columns = c.cols_accession)
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(len(df), 5)

        # Test with a file that doesn't exist
        df = read_file()
        self.assertIsNone(df)

        # Test with a file that the required columns don't exist
        df_error_accession = pd.DataFrame({
            'species_name': ['barley_growth_class', 'barley_growth_class', 'barley_growth_class', 'barley_growth_class', 'barley_growth_class'],
            'crop': [3, 3, 3, 3, 3],
            'landrace_group': ['3_1', '3_2', '3_2', '3_1', '3_1'],
            'country': ['GE', 'GE', 'TM', 'TM', 'TM'],
            'latitude': [41.45, 41.45, 37.95, 37.95, 37.2833],
            'longitude': [44.4667, 44.4667, 58.3667, 58.3667, 62.35],
            'Ext_ID': ['ICD_33', 'ICD_34', 'ICD_42', 'ICD_43', 'ICD_45'],
            'source_database': ['icarda', 'icarda', 'icarda', 'icarda', 'icarda'],
            'institution_name': ['ICARDA', 'ICARDA', 'ICARDA', 'ICARDA', 'ICARDA'],
            'accession_id': [16950, 16950, 16954, 16954, 16955]
        })
        
        with self.assertRaisesRegex(ValueError, "Missing required columns in accession.csv file: ext_id"):
            read_file(df_error_accession, 'accession.csv', c.cols_accession)

    def test_read_attributes_file(self):
        # Test with a DataFrame
        df = read_file(df = self.df_attributes, columns = c.cols_attribute)
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(len(df), 6)

        # Test with a file that doesn't exist
        df = read_file()
        self.assertIsNone(df)

        # Test with a file that the required columns don't exist
        df_error_attribute = pd.DataFrame({
            'key': ['height', 'drought tolerance', 'flowering time', 'height', 'drought tolerance', 'flowering time'],
            'Value': ['170 cm', 'moderate', '140 days', '165 cm', 'high', '135 days'],
            'accession': ['ICD_33_3', 'ICD_33_3', 'ICD_33_3', 'ICD_34_3', 'ICD_34_3', 'ICD_34_3']
        })
        
        with self.assertRaisesRegex(ValueError, "Missing required columns in attribute.csv file: value"):
            read_file(df_error_attribute, 'attribute.csv', c.cols_attribute)

    def test_import_accession(self):

        self.df_accessions.to_csv(os.path.join(project_dir_path, 'Inputs','accession.csv'))

        # Create and save two country objects
        georgia = Country(iso_2='GE', name='Georgia')
        georgia.save()
        turkmenistan = Country(iso_2='TM', name='Turkmenistan')
        turkmenistan.save()

        # create and save a crop object
        barley = Crop(ext_id='3', base_name='barley', name='Barley (growth class)', app_name='Barley (growth class) (alternative)')
        barley.save()

        spring_group = Group(ext_id="3_1", group_name="Spring", crop=barley)
        spring_group.save()

        winter_group = Group(ext_id="3_2", group_name="Winter", crop=barley)
        winter_group.save()
        
        with StringIO() as output:
            sys.stdout = output

            # Call the function you want to test
            import_accessions()

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
            import_accessions()

            # Get the output and reset stdout
            out = output.getvalue()
            sys.stdout = sys.__stdout__

            # Check that the output is correct
            self.assertIn('Processed 5 rows.', out)
            self.assertIn('Successfully saved 0 rows.', out)
            self.assertIn('Failed to save 5 rows.', out)

            self.assertTrue(os.path.isfile(os.path.join(project_dir_path, 'Outputs/accession_logs.xlsx')))


    def test_import_attributes(self):
        self.df_attributes.to_csv(os.path.join(project_dir_path, 'Inputs','attribute.csv'))
        with StringIO() as output:
            sys.stdout = output

            # Call the function you want to test
            import_attributes()

            # Get the output and reset stdout
            out = output.getvalue()
            sys.stdout = sys.__stdout__

            # Check that the output is correct
            self.assertIn('Processed 6 rows.', out)
            self.assertIn('Successfully saved 6 rows.', out)
            self.assertIn('No errors found', out)

        df_error_attributes = pd.DataFrame({
            'key': ['height', 'drought tolerance', 'flowering time', 'height', 'drought tolerance', 'flowering time'],
            'value': ['170 cm', 'moderate', '140 days', '165 cm', 'high', '135 days'],
            'accession': ['ICD_33', 'ICD_33', 'ICD_33', 'ICD_34', 'ICD_34', 'ICD_34']
        })

        df_error_attributes.to_csv(os.path.join(project_dir_path, 'Inputs','attribute.csv'))

        #Test import crops error
        with StringIO() as output:
            sys.stdout = output
            
            import_attributes()

            # Get the output and reset stdout
            out = output.getvalue()
            sys.stdout = sys.__stdout__

            # Check that the output is correct
            self.assertIn('Processed 6 rows.', out)
            self.assertIn('Successfully saved 0 rows.', out)
            self.assertIn('Failed to save 6 rows.', out)

            self.assertTrue(os.path.isfile(os.path.join(project_dir_path, 'Outputs/attribute_logs.xlsx')))


if __name__ == '__main__':
    unittest.main()

