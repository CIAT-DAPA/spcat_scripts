import os
import sys
import pandas as pd
from ormgap import Country
from tqdm import tqdm

dir_path = os.path.dirname(os.path.realpath(__file__))
config_dir_path = os.path.abspath(os.path.join(dir_path, '..'))
sys.path.append(config_dir_path)

import config as c

def read_countries_file( df = None ):
    countries = []
    if df is None:
        countries_file_path = os.path.join(c.path_inputs, "countries.csv")
        if os.path.isfile(countries_file_path):
            countries = pd.read_csv(countries_file_path, encoding='utf8', keep_default_na=False)
        else:
            return None
    else:
        countries = df

    # Verify that the required columns exist in the DataFrame
    missing_cols = set(c.cols_country) - set(countries.columns)

    if len(missing_cols) > 0:
        raise ValueError(f"Missing required columns in countries.csv file: {', '.join(missing_cols)}")

    return countries


def import_countries( data = None ):

    print('The process of importing countries has begun')

    try:
        countries = read_countries_file(data)
        if countries is None:
            print('Could not find countries.csv file')
            return
    except ValueError as e:
        print(f"Error reading countries.csv file: {str(e)}")
        return
    
    print('countries.csv file found')

    # Create a dataframe to store errors
    errores = pd.DataFrame(columns=['iso_2', 'name', 'error'])

    # Initialize counters
    success_count = 0
    error_count = 0

    # Traverse each row of the DataFrame
    for index, row in tqdm(countries.iterrows(), total=len(countries)):
        
        try:
            # Create a Country object with the row data
            country = Country(
                iso_2=str(row['iso_2']).strip(),
                name=str(row['name']).strip()
            )
    
            # Save the object in the database
            country.save()

            # Increment success counter
            success_count += 1

        except Exception as e:

            # Add the row with the error to the error dataframe
            errores = pd.concat([errores, pd.DataFrame(data={'iso_2': [str(row['iso_2'])], 'name': [str(row['name'])], 'error': [str(e)]})], ignore_index=True)

            # Increment error counter
            error_count += 1

    # Print results
    print(f"Processed {success_count + error_count} rows.")
    print(f"Successfully saved {success_count} rows.")
    print(f"Failed to save {error_count} rows.")

    # Saving the error dataframe in an Excel file
    if not errores.empty:
        try:
            errores.to_excel(os.path.join(c.path_outputs, "country_logs.xlsx"), index=False)
            print("Errors found, country_logs.xlsx file saved")
        except Exception as e:
            print("Errors found, but the file country_logs.xlsx could not be saved. Error:")
            print(e)
    else:
        print("No errors found")

if __name__ == '__main__':
    c.connect_db()
    import_countries()
            
