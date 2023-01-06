# -*- coding: utf-8 -*-
"""
Created on Tue Apr 19 19:49:53 2022

@author: rafle
"""

import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from app import app
import plotly.express as px
import pandas as pd
from dash.dependencies import Input, Output
import dash_uploader as du
import time
import folium
import geopandas as gpd

### Global variables
global geojsonLoaded 
global gpxLoaded 

geojsonLoaded = False
gpxLoaded = False
map2 = folium.Map()

### General functions, to be imported from another .py in further development

def calculateCentroid(geodataframe):
    allpolygons = geodataframe.dissolve()
    bounds = allpolygons.bounds
    minx = bounds.iloc[0]['minx']
    maxx = bounds.iloc[0]['maxx']
    miny = bounds.iloc[0]['miny']
    maxy = bounds.iloc[0]['maxy']
    xmean = (minx+maxx)/2
    ymean = (miny+maxy)/2
    return xmean, ymean, minx, miny,maxx, maxy

## Map styling functikon, move to 

def style_function(feature):
    #employed = employed_series.get(int(feature["id"][-5:]), None)
    return {
        "fillOpacity": 0.5,
        "weight": 0,
        #"fillColor": "#black" if employed is None else colorscale(employed),
    }

## Source 
PLOTLY_LOGO = "https://images.plot.ly/logo/new-branding/plotly-logomark.png"
##

##
#Data here
##
df = px.data.iris()
##Dataframe test 
       
df1 = pd.DataFrame({"a": [1, 2, 3, 4], "b": [2, 1, 5, 6], "c": ["x", "x", "y", "y"]})

####Map styles

def style_function1(feature):
    #print(feature)
    return{
        "fillOpacity": 0.65,
        "fillColor": "#E06666",
        "color": "#990000",
        "weight":"1"
    }
def style_function2(feature):
    #print(feature)
    return{
        "fillOpacity": 0.65,
        "fillColor": "#8fce00",
        "color": "#274e13",
        "weight":"1"

    }

NAVBAR_STYLE = {
    "position": "fixed",
    "top": "50px",
    "left": 0,
    "bottom": 0,
    "width": "350px",
    "height": "100%",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
    "display": "inline-block",
    
    
}

CONTENT_STYLE = {
    "width": "83%",
    "top":0,
    "margin-top":'50px',
    "margin-left": "339px",
    "padding-left": "0px",
    
    "margin-right": "0px",
    "margin-bottom": "0px",
    "position": "absolute",
}

#####################################
# Create Auxiliary Components Here
#####################################
def basic_scheme():
    row = html.Div([
        dbc.Row(dbc.Col(html.Div("Hello World"))),
        dbc.Row([
            dbc.Col(html.Div("Col 1")),
            dbc.Col(html.Div("Col 2")),
            dbc.Col(html.Div("Col 3")),
            dbc.Col(html.Div("Col 4"))
            ])
        ])
    return row

def head_bar():
    
    headBar = dbc.Navbar(
    dbc.Container(
        [
#            html.A(
                # Use row and col to control vertical alignment of logo / brand
                dbc.Row(
                    [
                        dbc.Col(html.Img(src=PLOTLY_LOGO, height="30px")),
                        dbc.Col(dbc.NavbarBrand("Procesador de velocidades", className="ms-2")),
                    ],
                    align="center"
#                ),

#                style={"textDecoration": "none"},
            ),
            dbc.NavbarToggler(id="navbar-toggler", n_clicks=0),
            dbc.Collapse(
                #search_bar,
                id="navbar-collapse",
                is_open=False,
                navbar=True,
            ),
        ]
    ),
    color="dark",
    dark=False,
    className="navbar navbar-expand-lg navbar-dark bg-primary",
    style = {'height' : '50px',
             'width' :'100%',
             "position": "fixed",
             }
    )
    
    return headBar

def nav_bar():
    '''
    Create navigation Bar
    '''
    
    navbar = html.Div(
        dbc.Col(
        [
            dbc.Row([
                dbc.Col(html.Img(src = PLOTLY_LOGO, width = "60px", height = "60px")),
                dbc.Col(html.H4("Speed Processing ", className="display-10", style ={'textAlign': 'left'}))             
                
                ]),
            html.Hr(),
            html.H5("Seleccione archivos de entrada"),

            du.Upload(id = 'loadZones2',
                      text = 'Cargue aquí las zonas y el archivo gpx, ambos deben estar proyectadas en WGS 84',
                      text_completed = 'Archivo cargado',
                      filetypes = ["geojson", "gpx"],
                      max_files = 2
                      ),
            html.Hr(),
            html.H5("Opciones de procesamiento"),
            dcc.Checklist(id = 'parameters', 
                          options = [{'label':'Diluir tracks','value':'dissolveTracks'},
                                     {'label':'Eliminar tiempos en ceros','value':'eliminateceropoints'}],
                          value = ['FunctionOptions']),
            dbc.Button("Borrar cache de archivos",id = 'resetFunction', color ='warning', className= 'me-1'),
            

        
            ],
        style = NAVBAR_STYLE,
        className= "card text-white bg-primary mb-3",
        width = 5
        )
        
        
        )
    return navbar

#graph 1
example_graph1 = px.scatter(df, x="sepal_length",y="sepal_width",color="species")

#graph 2
example_graph2 = px.histogram(df, x="sepal_length", color = "species",nbins=20)
example_graph2.update_layout(barmode='overlay')
example_graph2.update_traces(opacity=0.55)

#####################################
# Create Page Layouts Here
#####################################

### Layout 1
layout1 = html.Div([
    # create bootstrap grid 1Row x 2 cols
    dbc.Container([
        dbc.Row([
            html.H3("Visualizador de gráficos"),
            html.Hr()
            ]),
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.Div(
                            [
                            html.H4('Example Graph Page'),
                            #create tabs
                            dbc.Tabs(
                                [
                                    #graphs will go here eventually using callbacks
                                    dbc.Tab(label='graph1',tab_id='graph1'),
                                    dbc.Tab(label='graph2',tab_id='graph2')
                                ],
                                id="tabs",
                                active_tab='graph1',
                                ),
                            html.Div(id="tab-content",className="p-4")
                            ]
                        ),
                    ],
                    width=6 #half page
                ),
                
                dbc.Col(
                    [
                        html.H4('Additional Components here'),
                        html.P('Click on graph to display text', id='graph-text')
                    ],
                    width=6 #half page
                )
                
            ],
        ), 
    ]),
])


### Layout 2
layout2 = html.Div(
    [
        #html.H2('Map example'),
        #html.Hr(),
        html.Iframe( id = 'map', srcDoc = open('Example.html', 'r').read(), width = '100%', height = '700', style={'textAlign': 'center'}),
        dbc.Container(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                html.H4('Country'),
                                html.Hr(),
                                dcc.Dropdown(
                                    id='page2-dropdown',
                                    options=[
                                        {'label': '{}'.format(i), 'value': i} for i in [
                                        'United States', 'Canada', 'Mexico'
                                        ]
        ]
                                ),
                                html.Div(id='selected-dropdown')
                            ],
                            width=6
                        ),
                        dbc.Col(
                            [
                                html.H4('Fruit'),
                                html.Hr(),
                                dcc.RadioItems(
                                    id='page2-buttons',
                                    options = [
                                        {'label':'{}'.format(i), 'value': i} for i in [
                                        'Yes ', 'No ', 'Maybe '
                                        ]
                                    ]
                                ),
                                html.Div(id='selected-button')
                            ],
                        )
                    ]
                ),
            ]
        )
    ])


### Layout 3
layout3 = html.Div(
    dbc.Container([
        dbc.Row(html.Iframe( id = 'map1', srcDoc = open('Example.html', 'r').read(), height = '900', style={'textAlign': 'center'})),
        dbc.Row(dcc.Checklist(id = 'parameters',options = ['Filtrar velocidades mínimas','Disolver tracks'])),
        ## Download option
        html.Hr(),
        html.Button("Descargar resultados en formato excel", id = "resultado1"),
        dcc.Download(id = "download-results1"),
        html.P("Prueba Callback", id = "callback-output"),
        
 
        
        
        
         ],
        fluid = True,
        )
    )

## Callback example download button

@app.callback(
    Output("download-results1", "data"),
    Input("resultado1", "n_clicks"),
    prevent_initial_call = True, )

#Function with n_clicks as inputs,

def func(n_clicks):
    print("Hey")
    return dcc.send_data_frame(df.to_csv, "example.csv")

# Callback for loadzones 2
@du.callback(
    output = Output("callback-output", "children"),
    id = "loadZones2"
    )
def write_filename(status: du.UploadStatus):
    
    children = []
    for status in status.uploaded_files:
        characters = len(str(status))
        path = str(status)
        filetype = path[characters -3 : characters]
        line = html.Ul([html.Li(str(filetype))])
        children.append(line)
    return children
    #return html.Ul([html.Li(str(status.uploaded_files))])
@du.callback(
    output = Output("map1", "srcDoc"),
    #id =(["loadZones2","loadgpx"]),
    id = "loadZones2"
    )
def draw_map(status: du.UploadStatus): 
    
    for status in status.uploaded_files:
        characters = len(str(status))
        path = str(status)
        filetype = path[characters -3: characters]
        
        if(filetype == 'son'):
            geojsonfile = path
            global polygons
            polygons = gpd.read_file(path)
            geojsonLoaded = True
            ## Projection code that define epsg (necessary to redefine all)
            
            polygons = polygons.set_crs(epsg =3116, allow_override = True)
            polygons = polygons.to_crs(epsg=4326)
            
            ## Insert map routine for zones
            
            x, y, minx, miny, maxx, maxy = calculateCentroid(polygons)
            #map2 = folium.Map(location = [y, x])
            map2.location = [y,x]
            map2.fit_bounds([[miny,minx],[maxy, maxx]])
            ## Map iterations
            for _,r in polygons.iterrows():
                sim_geo = gpd.GeoSeries(r['geometry'])
                geo_j = sim_geo.to_json()
                if(r['Tipo'] == 'Borde'):          
                    geo_j = folium.GeoJson(data = geo_j, style_function = style_function1).add_to(map2)
                else:
                    geo_j = folium.GeoJson(data = geo_j, style_function = style_function2).add_to(map2)
                
            folium.LayerControl().add_to(map2)
            
            
            
        if(filetype == 'gpx'):
            global gpsPoints
            gpsPoints = gpd.read_file(path, layer = 'track_points')
            gpxLoaded = True       
            ## Create projection code for define projected epsg
            
            ## Insert map routine for gps points
            x, y, minx, miny, maxx, maxy = calculateCentroid(gpsPoints)
            #map2 = folium.Map(location = [y,x])
            map2.location = [y,x]
            map2.fit_bounds([[miny,minx],[maxy, maxx]])
            
            ## Map iterations (Customize)
            for _,r in gpsPoints.iterrows():
                sim_geo = gpd.GeoSeries(r['geometry'])
                popupText =  r['time']
                folium.CircleMarker(location = ([sim_geo.y, sim_geo.x]), tooltip = popupText, radius = 4).add_to(map2)
                #geo_j = sim_geo.to_json()
                #geo_j = folium.GeoJson(data = geo_j).add_to(map2)
                #geo_j = folium.CircleMarker(location = geo_j, radius =5).add_to(map2)
            folium.LayerControl().add_to(map2)    
    map2.save('zones.html')
            

            
    
    #filenames = str(geojsonfile)
    #polygons = gpd.read_file(filenames)
    #polygons = polygons.set_crs(epsg =3116, allow_override = True)
    #polygons = polygons.to_crs(epsg=4326)
    
    ## Calculate centroid for map
    #x, y, minx, miny, maxx, maxy = calculateCentroid(polygons)
    
    #map2 = folium.Map(location = [y, x])
    #map2.fit_bounds([[miny,minx],[maxy, maxx]])
    #for _,r in polygons.iterrows():
    #    sim_geo = gpd.GeoSeries(r['geometry'])
    #    geo_j = sim_geo.to_json()
    #    if(r['Tipo'] == 'Borde'):          
    #        geo_j = folium.GeoJson(data = geo_j, style_function = style_function1).add_to(map2)
    #    else:
    #        geo_j = folium.GeoJson(data = geo_j, style_function = style_function2).add_to(map2)
    #        folium
        
    map2.add_child(folium.LatLngPopup())
    map2.save('zones.html')
    map_export = open('zones.html', 'r').read()
    return(map_export)
#@du.callback(
#    output = Output("map1","srcDoc"),
#    id = "loadgpx",
#    )
#def add_gpx(status: du.UploadStatus, map2):
#    filenames = str(status.latest_file)
#    gpsPoints = gpd.read_file(filenames, layer = 'track_points')
#    folium.Marker(gpsPoints).add_to(map2)
#    map2.save('zones2.html')
#    map_export = open('zones2.html', 'r').read()
#    return(map_export)

    
    



    
