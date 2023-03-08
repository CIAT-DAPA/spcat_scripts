import os
import sys

dir_path = os.path.dirname(os.path.realpath(__file__))
config_dir_path = os.path.abspath(os.path.join(dir_path, '..'))
sys.path.append(config_dir_path)

import config as c
import pandas as pd
from ormgap import Country

if(os.path.isfile(os.path.join(c.path_inputs, "countries.csv"))):
    print('Found archive of countries.csv')
    countries = pd.read_csv(os.path.join(c.path_inputs, "countries.csv"),  encoding='utf8', keep_default_na=False)
    c.connect_db()

    # Create a dataframe to store errors
    errores = pd.DataFrame(columns=['iso_2', 'name', 'error'])

    # Traverse each row of the DataFrame
    for index, row in countries.iterrows():
        
        try:
            # Create a Country object with the row data
            country = Country(
                iso_2=str(row['iso_2']),
                name=str(row['name'])
            )
    
            # Save the object in the database
            country.save()

        except Exception as e:
            print('Errors found in row #' + str(index) + ', iso_2:' + str(row['iso_2']) + ', name:' + str(row['name']))
            # Add the row with the error to the error dataframe
            errores = pd.concat([errores, pd.DataFrame(data={'iso_2': [row['iso_2']], 'name': [row['name']], 'error': [str(e)]})], ignore_index=True)
    # Saving the error dataframe in an Excel file
    if not errores.empty:
        errores.to_excel(os.path.join(c.path_outputs, "country_logs.xlsx"), index=False)
        print("Errors found, country_logs.xlsx file saved")
    else:
        print("No errors found")
else: 
    print('No found archive of countries')
            
