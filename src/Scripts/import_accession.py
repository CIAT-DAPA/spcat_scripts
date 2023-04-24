import os
import glob
import sys

dir_path = os.path.dirname(os.path.realpath(__file__))
config_dir_path = os.path.abspath(os.path.join(dir_path, '..'))
sys.path.append(config_dir_path)

import config as c
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
from tqdm import tqdm
from ormgap import Crop, Group, Accession, Country

c.connect_db()

print('The process of importing accessions has begun')

#accession_files = glob.glob(os.path.join(c.path_inputs, "*_accession.csv"))

accession_files = glob.glob(c.path_inputs + '/*accession.csv')
accession_file_names = [os.path.basename(file) for file in accession_files]


# load country shapefile
countries = gpd.read_file(os.path.join(c.path_data, "Countries.zip"))

countries = countries.to_crs("EPSG:4326")

# select only the necessary columns (ISO2 and geometry)
countries = countries[["ISO2", "geometry"]]

if not len(accession_files) == 0:

    for file in accession_file_names:

        print(f'{file} file found')
        accessions = pd.read_csv(os.path.join(c.path_inputs, file),  encoding='utf8', keep_default_na=False)
        

        # Create a data frame to store errors
        errores = pd.DataFrame(columns=['ext_id', 'species_name', 'row', 'error'])

        # Initialize counters
        success_count = 0
        error_count = 0

        # creates a GeoDataFrame with the points corresponding to accessions
        points = [Point(xy) for xy in zip(accessions["longitude"], accessions["latitude"])]
        accessions_gdf = gpd.GeoDataFrame(accessions, geometry=points, crs="EPSG:4326")

        # join GeoDataFrames using the sjoin method
        accessions_by_country = gpd.sjoin(accessions_gdf, countries, how="left", predicate="within")

        # adds the column with the ISO2 for the corresponding country
        accessions["country"] = accessions_by_country["ISO2"]

        # Traverse each row of the DataFrame
        for index, row in tqdm(accessions.iterrows(), total=len(accessions)):
            
            try:

                crop = Crop.objects.get(ext_id=str(row['crop']))

                if crop is not None:

                    group = Group.objects.get(ext_id=str(row['landrace_group']))

                    if group is not None:

                        country = Country.objects.get(iso_2=str(row['country']))

                        if country is not None:

                            # Create a Accession object with the row data
                            accession = Accession(
                                ext_id=str(row['ext_id']).strip(),
                                species_name=str(row['species_name']).strip(),
                                crop=crop,
                                country=country,
                                landrace_group=group,
                                institution_name=str(row['institution_name']).strip(),
                                source_database=str(row['source_database']).strip(),
                                latitude=row['latitude'],
                                longitude=row['longitude'],
                                accession_id=str(row['accession_id']).strip()
                            )
                
                            # Save the object in the database
                            accession.save()

                            # Increment success counter
                            success_count += 1
                        else: 
                            errores = pd.concat([errores, pd.DataFrame(data={'ext_id': [str(row['ext_id'])], 'species_name': [str(row['species_name'])], 'row': [str(index + 2)],
                                'error': ['no country was found with that iso_2: ' + str(row['country'])]})], ignore_index=True)
                                
                            # Increment error counter
                            error_count += 1
                    else:
                        errores = pd.concat([errores, pd.DataFrame(data={'ext_id': [str(row['ext_id'])], 'species_name': [str(row['species_name'])], 'row': [str(index + 2)],
                            'error': ['no group was found with that ext_id: ' + str(row['landrace_group'])]})], ignore_index=True)
                        
                        # Increment error counter
                        error_count += 1
                else:
                    errores = pd.concat([errores, pd.DataFrame(data={'ext_id': [str(row['ext_id'])], 'species_name': [str(row['species_name'])], 'row': [str(index + 2)],
                        'error': ['no crop was found with that ext_id: ' + str(row['crop'])]})], ignore_index=True)

                    # Increment error counter
                    error_count += 1


            except Exception as e:
                #print('Errors found in row #' + str(index + 2) + ', ext_id:' + str(row['ext_id']) + ', name:' + str(row['name']))
                
                # Add the row with the error to the error dataframe
                errores = pd.concat([errores, pd.DataFrame(data={'ext_id': [str(row['ext_id'])], 'species_name': [str(row['species_name'])],
                    'row': [str(index + 2)], 'error': [str(e)]})], ignore_index=True)
                
                # Increment error counter
                error_count += 1

        # Print results
        print(f"Processed {success_count + error_count} rows.")
        print(f"Successfully saved {success_count} rows.")
        print(f"Failed to save {error_count} rows.")

        # Saving the error dataframe in an Excel file
        if not errores.empty:
            file_name = str(file).replace(".csv", "")
            try:
                errores.to_excel(os.path.join(c.path_outputs, f"{file_name}_logs.xlsx"), index=False)
                print(f"Errors found, {file_name}_logs.xlsx file saved")
            except Exception as e:            
                print(f"Errors found, but the file {file_name}_logs.xlsx could not be saved. Error:")
                print(e)
        else:
            print("No errors found") 
else: 
    print('Could not find accession.csv file')


attributes_files = glob.glob(c.path_inputs + '/*attribute.csv')
attributes_file_names = [os.path.basename(file) for file in attributes_files]

print('The process of importing attributes of accessions has begun')

if not len(attributes_files) == 0:

    for file in attributes_file_names:

        print(f'{file} file found')
        attributes = pd.read_csv(os.path.join(c.path_inputs, file),  encoding='utf8', keep_default_na=False)
        

        # Create a dataframe to store errors
        errores = pd.DataFrame(columns=['key', 'value', 'accession', 'row', 'error'])

        # Initialize counters
        success_count = 0
        error_count = 0

        # Traverse each row of the DataFrame
        for index, row in attributes.iterrows():
            
            try:

                accession = Accession.objects.get(ext_id=str(row['accession']))

                if accession is not None:
                    # add attribute to the accession found
                    accession.other_attributes[str(row['key']).strip()] = str(row['value']).strip()

                    # Save the object in the database
                    accession.save()

                    # Increment success counter
                    success_count += 1
                else:
                    errores = pd.concat([errores, pd.DataFrame(data={'key': [str(row['key'])], 'value': [str(row['value'])], 'accession': [str(row['accession'])], 'row': [str(index + 2)],
                        'error': ['no accession was found with that ext_id: ' + str(row['accession'])]})], ignore_index=True)

                    # Increment error counter
                    error_count += 1


            except Exception as e:
                #print('Errors found in row #' + str(index + 2) + ', ext_id:' + str(row['ext_id']) + ', name:' + str(row['name']))
                
                # Add the row with the error to the error dataframe
                errores = pd.concat([errores, pd.DataFrame(data={'key': [str(row['key'])], 'value': [str(row['value'])], 'accession': [str(row['accession'])], 
                    'row': [str(index + 2)], 'error': [str(e)]})], ignore_index=True)
                
                # Increment error counter
                error_count += 1

        # Print results
        print(f"Processed {success_count + error_count} rows.")
        print(f"Successfully saved {success_count} rows.")
        print(f"Failed to save {error_count} rows.")

        # Saving the error dataframe in an Excel file
        if not errores.empty:
            file_name = str(file).replace(".csv", "")
            try:
                errores.to_excel(os.path.join(c.path_outputs, f"{file_name}_logs.xlsx"), index=False)
                print(f"Errors found, {file_name}_logs.xlsx file saved")
            except Exception as e:            
                print(f"Errors found, but the file {file_name}_logs.xlsx could not be saved. Error:")
                print(e)
        else:
            print("No errors found") 
else: 
    print('Could not find attribute.csv file') 