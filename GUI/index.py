# -*- coding: utf-8 -*-
"""
Created on Tue May  3 20:54:40 2022

@author: rafle
"""

import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import dash_html_components as html

from app import app, server
## All the layouts elements are located here, including nav_bar, stles, and layouts
from layouts import nav_bar, layout1, layout2, layout3, CONTENT_STYLE
from layouts import head_bar, basic_scheme
import callbacks

app.layout = html.Div([    
    dcc.Location(id='url', refresh = False), #locates this structure to the url
    html.Div([
        head_bar(),
        nav_bar(),
        html.Div(id = 'page-content', style = CONTENT_STYLE)

        
#        dbc.Row(dbc.Col(head_bar())),
 #
#           dbc.Col([html.Div(nav_bar()),
#            html.Div(id = 'page-content', style = CONTENT_STYLE)         
#                     ])

            ])
        ])
            
    
    
#    dbc.Container([
#
#            dbc.Row([dbc.Col(head_bar())]),
#            dbc.Row([dbc.Col(nav_bar()),
#                     html.Div(id = 'page-content', style = CONTENT_STYLE)
#                     ]),
#            dbc.Row(basic_scheme())
#            
#        ])
    

    #nav_bar(),
    #html.Div(id = 'page-content', style = CONTENT_STYLE)



@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname'),])
def display_page(pathname):
    if pathname == '/':
        return layout1
    elif pathname == '/page1':
        return layout1
    elif pathname == '/page2':
        return layout2
    elif pathname == '/page3':
        return layout3
    else:
        return '404' #

if __name__ == '__main__':
    app.run_server(port=5000, host= '127.0.0.2',debug=True)