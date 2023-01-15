
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

#import geopandas as gpd
#from shapely.geometry import shape
df = pd.read_csv("listings.csv", low_memory=False)
df["price"] = df["price"].str.replace("$", "")
df["price"] = df["price"].str.replace(",", "")
df["price"] = pd.to_numeric(df["price"])

criteria = ['price', 'review_scores_value', 'number_of_reviews', 'review_scores_rating']
weights = [0.3, 0.2, 0.2, 0.3]

# calculate the overall rating for each property
df['overall_rating'] = df[criteria].mul(weights).sum(axis=1)
# Create a map visualization

fig = px.scatter_mapbox(df, lat='latitude', lon='longitude', text='name',
                  color='neighbourhood_group_cleansed',
                  color_discrete_sequence=px.colors.qualitative.G10,
                  zoom=10, height=450,
                  title="Scatter Mapbox of AirBnb Listings in NYC")
fig.update_layout(mapbox_style="open-street-map")
fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
room_type_counts = Counter(df['room_type'])
property_type_counts = Counter(df['property_type'])

# extract all amenities into one list
amenities = [item for sublist in [json.loads(x) for x in df['amenities']] for item in sublist]
wordcloud = WordCloud(width = 1600, height = 1600, 
                background_color ='white', 
                stopwords = None, 
                min_font_size = 10).generate(str(amenities)) 

# convert wordcloud to image
buf = io.BytesIO()
plt.imshow(wordcloud)
plt.axis('off')
plt.savefig(buf, format='png')
buf.seek(0)
encoded_image = base64.b64encode(buf.read()).decode('ascii')

trace = go.Heatmap(x = df['number_of_reviews'],
                   y = df['review_scores_rating'],
                   z = df['review_scores_value'],
                   colorscale = 'Viridis')

layout = html.Div([
    dcc.Graph(id='map', figure=fig),
    html.Div(className='row', children=[
        html.Div(className='col-4', children=[
            dcc.Graph(
                id='room-type-bar-chart',
                figure={
                    'data': [
                        go.Bar(
                            x=list(room_type_counts.keys()),
                            y=list(room_type_counts.values()),
                        )
                    ],
                    'layout': go.Layout(
                        title='Number of listings by room type in NYC',
                        xaxis={'title': 'Room Type'},
                        yaxis={'title': 'Number of listings'},
                        hovermode='closest'
                    )
                }
            ),]),
        html.Div(className='col-8', children=[
            dcc.Graph(
                id='property-type-chart',
                figure={
                    'data': [
                        go.Bar(
                            x=list(property_type_counts.keys()),
                            y=list(property_type_counts.values()),
                        )
                    ],
                    'layout': {
                        'title': 'Distribution of Listings by Property Type',
                        'xaxis': {'title': 'Property Type'},
                        'yaxis': {'title': 'Number of Listings'}
                    }
                }
            ),
        ])
    ]),
        dcc.Graph(
        id='property-radar-chart',
        figure={
            'data': [
                go.Scatterpolar(
                    r=df['overall_rating'],
                    theta=criteria,
                    fill='toself'
                )
            ],
            'layout': go.Layout(
                polar={'radialaxis': {'visible': False}},
                showlegend=False
            )
        }
    ),
    html.Div(className='row', children=[
        html.Div(className='col-8', children=[
            dcc.Graph(
                id='amenities-price-scatter',
                figure={
                    'data': [
                        {'x': [len(json.loads(x)) for x in df['amenities']], 'y': df['price'], 'type': 'scatter', 'mode': 'markers'}
                    ],
                    'layout': {
                        'title': 'Relationship between Number of Amenities and Price',
                        'xaxis': {'title': 'Number of Amenities'},
                        'yaxis': {'title': 'Price'}
                    }
                }
            )]),
        html.Div(className='col-4', children=[
            dcc.Graph(
                id='amenities-wordcloud',
                figure={
                    'data': [{'type': 'image',
                            'source': 'data:image/png;base64,{}'.format(encoded_image)}],
                    'layout': {'title': 'Amenities Wordcloud'}
                }
        )])
    ]),
    dcc.Graph(
        id='reviews-heatmap',
        figure={
            'data': [trace],
            'layout': {
                'title': 'Relationship between Review Scores and Number of Reviews',
                'xaxis': {'title': 'Number of Reviews'},
                'yaxis': {'title': 'Review Scores'}
            }
        }
    )


    
])