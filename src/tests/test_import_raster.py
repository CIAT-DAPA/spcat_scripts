import unittest
from geo.Geoserver import Geoserver
import requests

geoserver_url = 'https://isa.ciat.cgiar.org/geoserver2'
username = 'gapuser'
password = 'G4pUs3.R-2023am'

# create a geoserver instance
geo = Geoserver(geoserver_url, username=username, password=password)

class TestGeoserver(unittest.TestCase):

    def test_connection(self):
        """Method to test the connection to Geoserver"""
        try:
            auth = (geo.username, geo.password)
            response = requests.get(geo.service_url, auth=auth)
            if response.status_code == 200:
                return True
            else:
                return False
        except requests.exceptions.RequestException as e:
            print(e)
            return False

    def test_connection_successful(self):
        """Method to test if the connection to Geoserver was successful"""
        self.assertTrue(self.test_connection())

if __name__ == '__main__':
    unittest.main()
 
