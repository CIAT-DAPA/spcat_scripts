# Scripts

![GitHub release (latest by date)](https://img.shields.io/github/v/release/CIAT-DAPA/spcat_scripts) ![](https://img.shields.io/github/v/tag/CIAT-DAPA/spcat_scripts)

This repository is a collection of Python scripts that are used by the administrator user to load data into both the database and the GeoServer. These scripts are responsible for processing and loading data from external sources, such as CSV files, and preparing it for storage in the Gap database. In addition, they are also responsible for generating the mosaics of the gap analysis results and uploading them to the GeoServer.

**Important notes**

These Scripts must be used in conjunction with the ORM that was developed for the project, which you can find in this [repository](https://github.com/CIAT-DAPA/spcat_orm).


## Features

- [ormgap](https://github.com/CIAT-DAPA/spcat_orm)
- Pandas
- Supports Python 3.x

## Getting Started

To use the scripts, it is necessary to have an instance of MongoDB running, either locally or on a server that is accessible from the internet.

### Prerequisites

- Python 3.x
- MongoDB

### Project Structure

- `Inputs/`: This folder contains the input files from where data will be extracted.
- `Outputs/`: This folder contains the output files generated during the data import process, such as logs.
- `Scripts/`: This folder contains the Python scripts used for data import.
- `Data` : This folder contains the shapefile with the political divisions of the countries, this file is used by the script to import the accessions when checking the locations of the accessions.

## Installation

To use the import scripts, it is necessary to have an instance of MongoDB running. It is also recommended to create a virtual environment to work with this project and make sure that the dependencies are installed in the virtual environment instead of the global system.

1. Clone the repository
````sh
git clone https://github.com/CIAT-DAPA/spcat_scripts.git
````

2. Create a virtual environment
````sh
python -m venv env
````

3. Activate the virtual environment
- Linux
````sh
source env/bin/activate
````
- windows
````sh
env\Scripts\activate.bat
````
4. run this commands in order

- `pip install pipwin`: Install pipwin.
- `pipwin refresh`: refres pipwin.
- `pipwin install gdal`: Install GDAL library.
- `pip install geoserver-rest`: Install geoserver-rest library.


5. Install the required packages

````sh
pip install -r requirements.txt
````


## Usage

For the import of the data the scripts use different csv files from where the information will be imported and must be provided by the user, these files must be located in the `src/Inputs` folder, also a configuration file is used for the access information to the database which is `database.xlsx` this information must be configured by the user before starting the import process. If during the import of the data an error is generated with any of the data this information will be saved in excel files identified with the model name [model]_logs.xlsx for example `crop_logs.xlsx` this process does not stop the import, that is to say the error will be saved and the import of the rest of the data will continue. These log files will be stored in the `scr\Outputs` folder.

**Important notes**

It is important to remember that the csv files for importing must be in **utf8 encoding** format.
### Configuration

The parameters to be configured are found in the `database.xlsx` file. This file has information on how to connect to the database. Let's see what it has:


| Parameter|type  | Description|
|----------|------|------------|
|user      |string|Name of user to connect with database|
|password  |string|Password of the user to connect with database|
|host      |string|IP or hostname of the server in which is the database|
|port      |int   |Port in which is available the database in the server By default is: 27017|
|name_db   |string|Name of the database. By default is: dbgap|

### Import Crop

`import_crop.py` Script to import the crop data, as well as the corresponding subgroups into the database. For this two csv files are used, the first one identified with the name `crops.csv`, this file contains the information of the crops and the second file identified with the name `groups.csv` that contains the information of the subgroups of the crops.

You can import information of the groups without the need of a crops.csv file, you only have to take into account that the crop or crops to which the groups are related are already registered in the database. nomenclature uses the external crop identifier and a group identifier separated by an underscore, e.g. 12_2 where 12 is the ext_id of the crop and 2 represents the second subgroup of that crop.

**Inputs**

file crops.csv

| Column Name | Type   | Description                                   |
|-------------|--------|-----------------------------------------------|
| ext_id      | string | External ID of the crop. Mandatory and unique.|
| name        | string | Name of the crop. Mandatory.                  |
| base_name   | string | Base name of the crop.                        |
| app_name    | string | Application name of the crop. Mandatory.      |

file groups.csv

| Column Name | Type   | Description |
|-------------|--------|-------------|
| group_name  | string | Name of the group. Mandatory. |
| crop        | string | External ID of the crop to which the group belongs. Mandatory. |
| ext_id      | string | External identifier for the group. Mandatory and unique. |


**Outputs**

file crop_logs.xlsx

| Column Name | Description                   |
|-------------|-------------------------------|
| ext_id      | External ID of the crop.      |
| name        | Name of the crop.             |
| base_name   | Base name of the crop.        |
| app_name    | Application name of the crop. |
| error       | Error message that occurred while saving |

file group_logs.xlsx

| Column Name | Description |
|-------------|-------------|
| group_name  | Name of the group.|
| crop        | External ID of the crop to which the group belongs. |
| ext_id      | External identifier for the group. |
| error       | Error message that occurred while saving    |

-----------

### Import Conuntries

`import_country.py` Script to import countries data into the database. For this a csv file is used, the file name should be `countries.csv`

**Inputs**

file countries.csv

| Column Name | Type   | Description |
|-------------|--------|--------------------------------------------------------------|
| iso_2       | string | Two-letter ISO code for the country (ISO 3166-1 alpha-2). Mandatory and unique. |
| name        | string | Name of the country. Mandatory.|


**Outputs**

file country_logs.xlsx

| Column Name | Description |
|-------------|--------------------------------------------------------------|
| iso_2       | Two-letter ISO code for the country (ISO 3166-1 alpha-2).|
| name        | Name of the country. |
| error       | Error message that occurred while saving      |

-------------

### Import Accessions

`import_accession.py` Script to import accessions data into the database. For this, several csv files are used, so the script goes through the Inputs folder looking for the corresponding files, these files are identified by name and have two different structures, the first one identified with the name `{crop}_accession.csv`, this file contains the information of the accessions and the second file identified with the name `{crop}_attribute.csv` that contains the information of additional attributes for each one of the accessions.

**Inputs**

file {crop}_accession.csv

| Column Name      | Type    | Description                                                |
|------------------|---------|------------------------------------------------------------|
| species_name     | string  | Name of the species of the accession. Optional.            |
| crop             | string  | External ID of the crop to which the accession belongs. Mandatory.|
| landrace_group   | string  | External ID of the group to which the accession belongs. Mandatory. |
| country          | string  | Iso 2 of the country to which the accession belongs. Mandatory. |
| institution_name | string  | Name of the institution that holds the accession. Optional.|
| source_database  | string  | Name of the database where the accession was originally stored. Optional. |
| latitude         | float   | Latitude of the geographical location where the accession was collected. Mandatory. |
| longitude        | float   | Longitude of the geographical location where the accession was collected. Mandatory. |
| accession_id     | string  | Identifier of the accession in the source database. Optional.               |
| ext_id           | string  | External identifier for the accession. Mandatory and unique.|

file {crop}_attribute.csv

| Column Name | Type    | Description                |
|-------------|---------|----------------------------|
| key         | string  | attribute name. Mandatory. |
| value       | string  | attribute value. Mandatory.|
| accession   | string  | External ID of the accession to which the attribute belongs. Mandatory. |

**Outputs**

file {crop}_accession_logs.xlsx

| Column Name  | Description                              |
|--------------|------------------------------------------|
| species_name | Name of the species of the accession.    |
| ext_id       | External identifier for the accession.   |
| row          | row in which the accession is located in the original file |
| error        | Error message that occurred while saving |

file {crop}_attribute_logs.xlsx

| Column Name | Description                                                 |
|-------------|-------------------------------------------------------------|
| key         | attribute name                                              |
| value       | attribute value                                             |
| accession   | External ID of the accession to which the attribute belongs.|
| row         | row in which the attribute is located in the original file  |
| error       | Error message that occurred while saving                    |

--------------

### Import Raster

**Inputs**

`import_raster.py` Script to import raster files in geotiff format to a server (geoserver), this script goes to a folder where the raster files will be stored, the script generates a connection to the geoserver, reads each file in the folder and publishes them to the geoserver.
This script uses certain variables that must be modified by the user, which are listed below:

- `geoserver_url`: here you will put the url where your geoserver is hosted, for example: `http://127.0.0.1:8080/geoserver`
- `username`: username with which you enter the goserver, for example: `admin`
- `password`: password with which you enter the goserver, for example: `geoserver`
- `workspace`: workspace of the geoserver to which you want the raster files to be published, for example: `my_workspace`  this workspace must be previously created on the geoserver
- `image_directory`: here you will put the path where the folder with the raster files is located, you can use an absolute path, for example: `C:/ScripRaster/raster` or you can use a relative path if you want to place the folder inside the project, for example: `../rasters` 

**Outputs**

After you have configured everything, you can run the file, with the python command `import_raster.py` If everything is correct in the console, the following messages will be printed, `number of files in the folder` rasters have been uploaded to the Geoserver and Failed to upload `number of files that failed to import` rasters.

After this you can verify that the files have been uploaded successfully in the layer preview window on your geoserver

If there is an error in the import, a file named `erros_logs.xlsx` will be created with the error description.
