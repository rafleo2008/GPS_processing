_GPS_processing_
Tool that automatize GPS speed processing

# Overview

This tool uses .gpx point files to calculate speeds in specific zones. The zones must be pre-defined using a GIS tool like ArcGIS or QGIS. This tool will be useful for monitoring speeds in specific zones and processing several tracks in the same area and per mode.

# Previous requirements

You must have installed these libraries
 
 - geopandas
 - pandas
 - dash
 
# Inputs

- gpx file with tracking positions
- zones shapefile (example here)

# Processing

This tool follows the next procedure

1. Identify track points inside zones
2. Identify flow direction
3. Group by zone
4. Export selection by trip, zone and direction
# Outputs

1. .cvs files containing results (further developments will use excel)

# Main issues

1. Check examples before updating materials
2. Dont forget to check epsg data, must be equal

## Hello 1

