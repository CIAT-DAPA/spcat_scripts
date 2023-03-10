import sys
import os
import pandas as pd
from mongoengine import connect

dir_path = os.path.dirname(os.path.realpath(__file__))
path_inputs = os.path.abspath(os.path.join(dir_path, 'Inputs'))
path_outputs = os.path.abspath(os.path.join(dir_path, 'Outputs'))
path_database = os.path.abspath(os.path.join(dir_path, 'database.xlsx'))

if not os.path.exists(path_outputs):
    os.mkdir(path_outputs)

try:
    database = pd.read_excel(path_database)
except Exception as e:
    print('Problem reading database.xlsx file')
    print(e)
    sys.exit(1)

cols_country = ['iso_2', 'name']
cols_crop = ['ext_id', 'name', 'base_name', 'app_name']
cols_group = ['group_name', 'crop', 'ext_id']
cols_accession = ['species_name', 'crop', 'landrace_group', 'institution_name', 'source_database', 'latitude', 'longitude', 'accession_id']


def get_parameter(name):    
    value = database[database.parameter == name].iloc[0]['value'] 
    return str(value)

def connect_db():
    try:
        host = get_parameter('host')
        port = get_parameter('port')
        user = get_parameter('user')
        password = get_parameter('password')
        name_db = get_parameter('name_db')
        db_url = "mongodb://" + user + ":" + password + "@" + host + ":" + port
        connection = connect(host=db_url, db=name_db)
        connection.server_info()
        print("Connection to database successful!")
        return connection
    except Exception as e:        
        print("Error connecting to MongoDB:")
        print(e)
        print("Please check the parameters in the file database.xlsx")
        sys.exit(1)
