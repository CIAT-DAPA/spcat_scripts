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
        # Creamos una base de datos de prueba en memoria utilizando pandas
        self.test_database = pd.DataFrame({
            'parameter': ['host', 'port', 'user', 'password', 'name_db'],
            'value': ['localhost', '27017', 'testuser', 'testpassword', 'testdb']
        })
        
        # Mockeamos la función connect de mongoengine para que no se conecte realmente a una base de datos
        self.patcher = patch('mongoengine.connect')
        self.mock_connect = self.patcher.start()
        
    def tearDown(self):
        # Detenemos el mock de la función connect
        self.patcher.stop()
        
    def test_get_parameter(self):
        # Verificamos que la función get_parameter retorne el valor correcto
        parameter_name = 'user'
        expected_value = 'testuser'
        actual_value = get_parameter(parameter_name, df=self.test_database)
        self.assertEqual(expected_value, actual_value)
        
    def test_connect_db_failure(self):
        # Verificamos que la función connect_db levante una excepción en caso de error
        self.mock_connect.side_effect = Exception('Test exception')
        
        with self.assertRaises(Exception):
            connect_db(database=self.test_database)
