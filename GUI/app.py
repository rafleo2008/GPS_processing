# -*- coding: utf-8 -*-
"""
Created on Tue May  3 20:52:41 2022

@author: rafle
"""

from dash import Dash, html, dcc
import plotly.express as px
import pandas as pd
import folium
import dash_bootstrap_components as dbc
import dash_uploader as du

NY_COORDINATE = (40.7128, -74.0060)


### Example of folium map

#my_map = folium.Map(location= NY_COORDINATE, tiles = 'Stamen Toner', zoom_start = 2, attr = 'My World')
my_map = folium.Map(location= NY_COORDINATE, zoom_start = 3, attr = 'My World')
#my_map = folium.Map(location= NY_COORDINATE, zoom_start = 12)
my_map.save('Example.html')


#app = Dash(__name__)

app = Dash(__name__, external_stylesheets = [dbc.themes.LITERA])
du.configure_upload(app,folder = r'C:\tmp\uploads' , use_upload_id=True, upload_api=None, http_request_handler=None)
server = app.server

