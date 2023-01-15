import dash
import pandas as pd
import numpy as np
import plotly.express as px
from plotly import graph_objs as go
from plotly.graph_objs import *
from dash.dependencies import Input, Output, State
from dash import dcc, callback, Dash
from dash import html
from dash import dash_table
import dash_bootstrap_components as dbc
import app

airbnb_data = pd.read_csv("/Users/ileanacrudu/Downloads/VIS/airbnb_open_data.csv", low_memory=False)
airbnb_data["price"] = airbnb_data["price"].str.replace("$", "")
airbnb_data["price"] = airbnb_data["price"].str.replace(",", "")
airbnb_data["service fee"] = airbnb_data["service fee"].str.replace("$", "")
airbnb_data["price"] = airbnb_data["price"].astype('Int64')
nbh = airbnb_data["neighbourhood"].dropna().unique().tolist()
card1 = dbc.Card(children=[
    dbc.CardBody([
        html.H4("Select a neighbourhood", className="card-title",id="card_num1"),
        html.P("", className="card-text",id="card_text1")
    ])
],
    style={'display': 'inline-block',
           'width': '100%',
           'text-align': 'center',
           'color':'white',
           'background-color': 'rgba(37, 150, 190)'},
    outline=True)

layout1 = html.Div(
    children =[
        html.H3("AirBnb Data"),
        dcc.Dropdown(options = nbh, id = "nbh_dropdown", multi=False, placeholder="Select a neighborhood"),
        card1,
        dcc.Graph(id='nbh_graph'),
        dcc.Graph(id = "room_graph"),
        dcc.Graph(id = "year_graph"),
        dcc.Graph(id = "violin")])


@callback(
   [
    Output('card_num1','children'),
    Output('card_text1','children'),
    Output("nbh_graph", "figure"),
    Output("room_graph", "figure"),
    Output("year_graph", "figure"),
    Output("violin", "figure")
   ],
    Input('nbh_dropdown','value')
)
def update_card(nbh_select):
    df = airbnb_data
    n = nbh
    if nbh_select != "nan":
        nbh_df = df[df["neighbourhood"]==nbh_select].sort_values(by =["price"])
        output1 = nbh_select + " has a total of " + str(nbh_df["id"].count()) + " properties listed"
        output2 = "Average property price per night: " +  str(round(nbh_df["price"].astype(float).mean(),2)) + "$"
        fig = px.histogram(nbh_df, x = "price", nbins = 30,width=1400,height=1400)
        room_fig = px.pie(nbh_df, names = "room type", width=1400, height=1400)
        year_fig = px.histogram(nbh_df, x = "Construction year", nbins = 30, width=1400, height=1400)
        vio = px.violin(nbh_df,y ="availability 365",box=True, title = "Violin plot of Availability",width=1400, height=1400)


    else:
        output1 =  "New York City has a total of " + str(df["id"].count()) + " properties listed"
        output2 = "Average property price per night: " +  str(round(df["price"].astype(float).mean(),2)) + "$"
        fig = px.histogram(df, x = "price", nbins = 30, color_discrete_sequence=['indianred'])
        room_fig = px.pie(df, values = "id", names = "room type")
        year_fig = px.histogram(df, x = "Construction year", nbins = 30)
        vio = px.violin(df,y ="availability 365", box=True,title = "Violin plot of Availability")
        


    return output1, output2, fig, room_fig,year_fig, vio


