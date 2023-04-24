import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import unittest
from unittest.mock import patch, Mock
import pandas as pd

# Importamos las funciones del script que queremos probar
from config import get_parameter, connect_db

class ConfiguracionTestCase(unittest.TestCase):
    def setUp(self):
        # Create an in-memory test database using pandas
        self.test_database = pd.DataFrame({
            'parameter': ['host', 'port', 'user', 'password', 'name_db'],
            'value': ['localhost', '27017', 'testuser', 'testpassword', 'testdb']
        })
        
        # Mess up the connect function of mongoengine so that it doesn't actually connect to a database
        self.patcher = patch('mongoengine.connect')
        self.mock_connect = self.patcher.start()
        
    def tearDown(self):
        # Stop the mock of the connect function
        self.patcher.stop()
        
    def test_get_parameter(self):
        # Verify that the get_parameter function returns the correct value
        parameter_name = 'user'
        expected_value = 'testuser'
        actual_value = get_parameter(parameter_name, df=self.test_database)
        self.assertEqual(expected_value, actual_value)
        
    def test_connect_db_failure(self):
        # Verify that the connect_db function raises an exception in case of error
        self.mock_connect.side_effect = Exception('Test exception')
        
        with self.assertRaises(Exception):
            connect_db(database=self.test_database)
