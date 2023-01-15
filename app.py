import dash
from dash import dcc, callback, Dash
import pandas as pd
import numpy as np
import plotly.express as px
from plotly import graph_objs as go
from plotly.graph_objs import *
from dash.dependencies import Input, Output, State
from dash import html
from dash import dash_table
import page1
import page2
import page3
import landing
import dash_bootstrap_components as dbc



app = Dash(__name__, suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.BOOTSTRAP])

server = app.server

app.layout = html.Div([
    

    dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Neighbourhood Data", href="page2")),
        dbc.DropdownMenu(
            children=[
                dbc.DropdownMenuItem("More", header=True),
                dbc.DropdownMenuItem("NYC AirBnB Data", href="/page1"),
                dbc.DropdownMenuItem("Github Code", href="/page3"),
                #dbc.DropdownMenuItem("Q&A", href="#"),
                #dbc.DropdownMenuItem("Github Code", href="#")
            ],
            nav=True,
            in_navbar=True,
            label="More",
        )
    ]
),
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')

])
@app.callback(Output('page-content', 'children'),
              Input('url', 'pathname'))
def display_page(pathname):
    if pathname == '/page1':
        return page1.layout
    elif pathname == '/page2':
        return page2.layout1
    elif pathname =="/page3":
        return page3.layout2
    else:
        return landing.layout

if __name__ == '__main__':  
    app.run_server(debug = True) 