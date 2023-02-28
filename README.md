# Scripts

![GitHub release (latest by date)](https://img.shields.io/github/v/release/CIAT-DAPA/spcat_scripts) ![](https://img.shields.io/github/v/tag/CIAT-DAPA/spcat_scripts)

This repository is a collection of Python scripts that are used by the administrator user to load data into both the database and the GeoServer. These scripts are responsible for processing and loading data from external sources, such as CSV files, and preparing it for storage in the Gap database. In addition, they are also responsible for generating the mosaics of the gap analysis results and uploading them to the GeoServer.

**Important notes**

These Scripts must be used in conjunction with the ORM that was developed for the project, which you can find in this [repository](https://github.com/CIAT-DAPA/spcat_orm).

[TOCM]

[TOC]

## Feacture

### Import Crop

Script to import the crop data, as well as the corresponding subgroups into the database

**Inputs**
file CSV

-----------

### Import Conuntries

Script to import countries data into the database

**Inputs**

file CSV

-------------

### Import Accessions

Script to import accession data into the database

**Inputs**

--------------

### Import Raster

**Inputs**
Rasters in geotiff format
