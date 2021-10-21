## Preparación y ejecución de función de gps

import pandas as pd
import geopandas as gpd
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

procesarGPS("Recorrido Carolina.gpx", "Geofences.shp", "Buses calzada lenta",3)