import sys
import os
import pandas as pd
from mongoengine import connect

dir_path = os.path.dirname(os.path.realpath(__file__))
path_inputs = os.path.abspath(os.path.join(dir_path, 'Inputs'))
path_outputs = os.path.abspath(os.path.join(dir_path, 'Outputs'))
path_database = os.path.abspath(os.path.join(dir_path, 'database.xlsx'))
database = pd.read_excel(path_database)


cols_country = ['iso_2', 'name']
cols_crop = ['ext_id', 'name', 'base_name', 'app_name']
cols_group = ['group_name', 'crop', 'ext_id']
cols_accession = ['species_name', 'crop', 'landrace_group', 'institution_name', 'source_database', 'latitude', 'longitude', 'accession_id']


def get_parameter(name):    
    value = database[database.parameter == name].iloc[0]['value'] 
    return str(value)

def connect_db():
    host = get_parameter('host')
    port = get_parameter('port')
    user = get_parameter('user')
    password = get_parameter('password')
    name_db = get_parameter('name_db')
    db_url = "mongodb://" + user + ":" + password + "@" + host + ":" + port
    return connect(host=db_url, db=name_db)
