import sys
import os
import pandas as pd
from mongoengine import connect

dir_path = os.path.dirname(os.path.realpath(__file__))
path_inputs = os.path.abspath(os.path.join(dir_path, 'Inputs'))
path_outputs = os.path.abspath(os.path.join(dir_path, 'Outputs'))
path_database = os.path.abspath(os.path.join(dir_path, 'database.xlsx'))
path_data = os.path.abspath(os.path.join(dir_path, 'Data'))

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
cols_accession = ['ext_id', 'species_name', 'crop', 'country', 'landrace_group', 'institution_name', 'source_database', 'latitude', 'longitude', 'accession_id']
cols_attribute = ['key', 'value', 'accession']


def get_parameter(name, df=database):
    value = df[df.parameter == name].iloc[0]['value']
    if pd.isnull(value):
        return None
    else:
        return str(value)

def connect_db():
    try:
        print("Connecting to database, please wait...")
        host = get_parameter('host')
        port = get_parameter('port')
        user = get_parameter('user')
        password = get_parameter('password')
        name_db = get_parameter('name_db')
        db_url = "mongodb://"
        if user and password:
            db_url += user + ":" + password + "@"
        db_url += host + ":" + port
        print('database: ', db_url)
        connection = connect(host=db_url, db=name_db)
        connection.server_info()
        print("Connection to database successful!")
        return connection
    except Exception as e:        
        print("Error connecting to MongoDB:")
        print(e)
        print("Please check the parameters in the file database.xlsx or the operation of the database")
        sys.exit(1)
