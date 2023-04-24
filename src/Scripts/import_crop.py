import os
import sys

dir_path = os.path.dirname(os.path.realpath(__file__))
config_dir_path = os.path.abspath(os.path.join(dir_path, '..'))
sys.path.append(config_dir_path)

import config as c
import pandas as pd
from ormgap import Crop, Group
from tqdm import tqdm

def read_file( df = None, name_file = '', columns = [] ):
    file = []
    if df is not None:
        file = df
    else:
        file_path = os.path.join(c.path_inputs, name_file)
        if os.path.isfile(file_path):
            file = pd.read_csv(file_path, encoding='utf8', keep_default_na=False)
        else:
            return None

    # Verify that the required columns exist in the DataFrame
    missing_cols = set(columns) - set(file.columns)

    if len(missing_cols) > 0:
        raise ValueError(f"Missing required columns in {name_file} file: {', '.join(missing_cols)}")
    
    return file

def import_crops( data = None):

    print('The process of importing crops has begun')

    try:
        crops = read_file(data, 'crops.csv', c.cols_crop)
        if crops is None:
            print('Could not find crops.csv file')
            return
    except ValueError as e:
        print(f"Error reading crops.csv file: {str(e)}")
        return

    # Create a dataframe to store errors
    errores = pd.DataFrame(columns=['ext_id', 'name', 'base_name', 'app_name', 'error'])

    # Initialize counters
    success_count = 0
    error_count = 0

    # Traverse each row of the DataFrame
    for index, row in tqdm(crops.iterrows(), total=len(crops)):
        
        try:
            # Create a Crop object with the row data
            crop = Crop(
                ext_id=str(row['ext_id']).strip(),
                name=str(row['name']).strip(),
                base_name=str(row['base_name']).strip(),
                app_name=str(row['app_name']).strip()
            )
    
            # Save the object in the database
            crop.save()

            # Increment success counter
            success_count += 1

        except Exception as e:
                        
            # Add the row with the error to the error dataframe
            errores = pd.concat([errores, pd.DataFrame(data={'ext_id': [str(row['ext_id'])], 'name': [str(row['name'])], 'base_name': [str(row['base_name'])],
                'app_name' : [str(row['app_name'])], 'error': [str(e)]})], ignore_index=True)
            
            # Increment error counter
            error_count += 1

    # Print results
    print(f"Processed {success_count + error_count} rows.")
    print(f"Successfully saved {success_count} rows.")
    print(f"Failed to save {error_count} rows.")

    # Saving the error dataframe in an Excel file
    if not errores.empty:
        try:
            errores.to_excel(os.path.join(c.path_outputs, "crop_logs.xlsx"), index=False)
            print("Errors found, crop_logs.xlsx file saved")
        except Exception as e:            
            print("Errors found, but the file crop_logs.xlsx could not be saved. Error:")
            print(e)
    else:
        print("No errors found")

def import_groups( data = None):
    print('The process of importing groups has begun')

    try:
        groups = read_file(data, 'groups.csv', c.cols_group)
        if groups is None:
            print('Could not find groups.csv file')
            return
    except ValueError as e:
        print(f"Error reading groups.csv file: {str(e)}")
        return

    # Create a dataframe to store errors
    errores = pd.DataFrame(columns=['ext_id', 'crop', 'group_name', 'error'])

    # Initialize counters
    success_count = 0
    error_count = 0

    # Traverse each row of the DataFrame
    for index, row in tqdm(groups.iterrows(), total=len(groups)):
        
        try:
            crop = Crop.objects.get(ext_id=str(row['crop']))

            if crop is not None:

                # Create a Group object with the row data
                group = Group(
                    ext_id=str(row['ext_id']).strip(),
                    crop=crop,
                    group_name=str(row['group_name']).strip()
                )
        
                # Save the object in the database
                group.save()

                # Increment success counter
                success_count += 1

            else:
                errores = pd.concat([errores, pd.DataFrame(data={'ext_id': [str(row['ext_id'])], 'group_name': [str(row['group_name'])], 'crop': [str(row['crop'])],
                'error': ['no crop was found with that ext_id: ' + str(row['crop'])]})], ignore_index=True)
                print('Errors found in row #' + str(index + 2) + ', ext_id:' + str(row['ext_id']) + ', group_name:' + str(row['group_name']))
                # Increment error counter
                error_count += 1

        except Exception as e:
            
            # Add the row with the error to the error dataframe
            errores = pd.concat([errores, pd.DataFrame(data={'ext_id': [str(row['ext_id'])], 'group_name': [str(row['group_name'])], 'crop': [str(row['crop'])],
                'error': [str(e)]})], ignore_index=True)
    
            # Increment error counter
            error_count += 1

    # Print results
    print(f"Processed {success_count + error_count} rows.")
    print(f"Successfully saved {success_count} rows.")
    print(f"Failed to save {error_count} rows.")

    # Saving the error dataframe in an Excel file
    if not errores.empty:
        try:        
            errores.to_excel(os.path.join(c.path_outputs, "group_logs.xlsx"), index=False)
            print("Errors found, group_logs.xlsx file saved")
        except Exception as e:
            print("Errors found, but the file group_logs.xlsx could not be saved. Error:")
            print(e)
    else:
        print("No errors found")


if __name__ == '__main__':
    c.connect_db()
    import_crops()
    import_groups()