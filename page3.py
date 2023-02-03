
import pandas
import dash
import numpy as np 
import matplotlib.pyplot as plt
import seaborn as sns
from shapely import wkt
import dash_bootstrap_components as dbc
import plotly.express as px
from plotly import graph_objs as go
from plotly.graph_objs import *
from dash.dependencies import Input, Output, State
from dash import dcc, html, Input, Output, callback
import app
from dash import dash_table
import pandas as pd
from collections import Counter
import json
import io
import base64
from wordcloud import WordCloud

airbnb_data = pd.read_csv("/Users/ileanacrudu/Downloads/VIS/airbnb_open_data.csv", low_memory=False)
df = pd.read_csv("listings.csv", low_memory=False)
df["price"] = df["price"].str.replace("$", "")
df["price"] = df["price"].str.replace(",", "")
df["price"] = pd.to_numeric(df["price"])
df['host_acceptance_rate'] = df['host_acceptance_rate'].str.rstrip('%').astype('float') / 100.0
df["log_price"] = np.log2(df["price"]).round(2)
df["log10_price"] = np.log10(df["price"]).round(2)


layout_host = html.Div([
    
])