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

airbnb_data = pd.read_csv("airbnb_open_data.csv", low_memory=False)
airbnb_data["price"] = airbnb_data["price"].str.replace("$", "")
airbnb_data["price"] = airbnb_data["price"].str.replace(",", "")
airbnb_data["service fee"] = airbnb_data["service fee"].str.replace("$", "")
airbnb_data["service fee"] = airbnb_data["service fee"].str.replace(",", "")

airbnb_data["price"] = airbnb_data["price"].astype('Int64')
airbnb_data["service fee"] = airbnb_data["service fee"].astype('Int64')

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
        html.Div(className='row', children=[
            html.Div(className='col-4', children=[
                dcc.Graph(id='nbh_graph'),]),
            html.Div(className='col-4', children=[
                dcc.Graph(id='service_fee_graph'),]),
            html.Div(className='col-4', children=[
            
                dcc.Graph(id = "room_graph"),])
        ]),
        dcc.Graph(id = "violin")])


@callback(
   [
    Output('card_num1','children'),
    Output('card_text1','children'),
    Output("nbh_graph", "figure"),
    Output("service_fee_graph", "figure"),
    Output("room_graph", "figure"),
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
        fig = px.histogram(nbh_df, x = "price",color="room type", nbins = 30,title = "Price distribution")
        fig2 = px.histogram(nbh_df, x = "service fee",color="room type", nbins = 30, title= "Service Fee distribution")

        room_fig = px.pie(nbh_df, names = "room type", title= "% per room type")
        vio = px.violin(nbh_df,x = "room type",y ="price",color ="room type",box=True, title = "Violin plot of Prices per Night")


    else:
        output1 =  "New York City has a total of " + str(df["id"].count()) + " properties listed"
        output2 = "Average property price per night: " +  str(round(df["price"].astype(float).mean(),2)) + "$"
        fig = px.histogram(df, x = "price", nbins = 30, color="room type", color_discrete_sequence=['indianred'])
        fig2 = px.histogram(nbh_df, x = "service fee",color="room type", nbins = 30)

        room_fig = px.pie(df, values = "id", names = "room type")
        vio = px.violin(df,y ="price", color = "room type",box=True,title = "Violin plot of Price")
        


    return output1, output2, fig, fig2, room_fig,vio


