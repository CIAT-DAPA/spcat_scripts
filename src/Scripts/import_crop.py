import os
import sys

dir_path = os.path.dirname(os.path.realpath(__file__))
config_dir_path = os.path.abspath(os.path.join(dir_path, '..'))
sys.path.append(config_dir_path)

import config as c
import pandas as pd
from ormgap import Crop, Group

c.connect_db()

print('The process of importing crops has begun')

if(os.path.isfile(os.path.join(c.path_inputs, "crops.csv"))):
    print('crops.csv file found')
    crops = pd.read_csv(os.path.join(c.path_inputs, "crops.csv"),  encoding='utf8', keep_default_na=False)
    

    # Create a dataframe to store errors
    errores = pd.DataFrame(columns=['ext_id', 'name', 'base_name', 'app_name', 'error'])

    # Initialize counters
    success_count = 0
    error_count = 0

    # Traverse each row of the DataFrame
    for index, row in crops.iterrows():
        
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
            print('Errors found in row #' + str(index + 2) + ', ext_id:' + str(row['ext_id']) + ', name:' + str(row['name']))
            
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
else: 
    print('Could not find crops.csv file')

print('The process of importing groups has begun')

if(os.path.isfile(os.path.join(c.path_inputs, "groups.csv"))):
    print('groups.csv file found')
    groups = pd.read_csv(os.path.join(c.path_inputs, "groups.csv"),  encoding='utf8', keep_default_na=False)

    # Create a dataframe to store errors
    errores = pd.DataFrame(columns=['ext_id', 'crop', 'group_name', 'error'])

    # Initialize counters
    success_count = 0
    error_count = 0

    # Traverse each row of the DataFrame
    for index, row in groups.iterrows():
        
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
            print('Errors found in row #' + str(index + 2) + ', ext_id:' + str(row['ext_id']) + ', group_name:' + str(row['group_name']))
            
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
else: 
    print('Could not find groups.csv file')