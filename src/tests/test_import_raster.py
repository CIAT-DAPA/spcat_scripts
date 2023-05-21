import unittest
#from geo.Geoserver import Geoserver
import requests

geoserver_url = 'https://isa.ciat.cgiar.org/geoserver2'
username = 'gapuser'
password = 'pass'

# create a geoserver instance
#geo = Geoserver(geoserver_url, username=username, password=password)

class TestGeoserver(unittest.TestCase):

    def test_connection(self):
        response =requests.get(geoserver_url)
        print(response)
        self.assertEqual(200, response.status_code)
        """ try:
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
        self.assertTrue(self.test_connection()) """

if __name__ == '__main__':
    unittest.main()
 
