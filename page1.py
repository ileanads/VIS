
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
from plotly.subplots import make_subplots

#import geopandas as gpd
#from shapely.geometry import shape
df = pd.read_csv("listings.csv", low_memory=False)
df["price"] = df["price"].str.replace("$", "")
df["price"] = df["price"].str.replace(",", "")
df["price"] = pd.to_numeric(df["price"])
df['host_acceptance_rate'] = df['host_acceptance_rate'].str.rstrip('%').astype('float') / 100.0
df["log_price"] = np.log2(df["price"]).round(2)
df["log10_price"] = np.log10(df["price"]).round(2)


# calculate the overall rating for each property
df["accommodates"] = pd.to_numeric(df['accommodates'])
# Create a map visualization

room_type_counts = Counter(df['room_type'])
property_type_counts = Counter(df['property_type'])
non_na = df.dropna(subset=['host_listings_count', 'host_total_listings_count'])
non_na["host_listings_count"] = non_na["host_listings_count"].astype(int)
non_na["host_total_listings_count"] = non_na["host_total_listings_count"].astype(int)
neighborhood_reviews = df.groupby(["neighbourhood_group_cleansed", "room_type"]).mean()["review_scores_rating"].round(1)
neighborhood_reviews = neighborhood_reviews.dropna()
n_reviews = neighborhood_reviews.reset_index()



options_price = [
    {'label': 'Price', 'value': 'price'},
    {'label': 'Log of Price', 'value': 'log_price'},
    {"label": "Density Map", "value": "density"}
]




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
#price vs accomodates
df2 = df.dropna(subset=["accommodates"])
df2["price"] =pd.to_numeric(df2["price"])
df2["accommodates"] =pd.to_numeric(df2["accommodates"])
mean_df = df.groupby("neighbourhood_group_cleansed")[["review_scores_communication","review_scores_rating", "review_scores_cleanliness", "review_scores_checkin", "review_scores_location", "review_scores_value"]].mean().round(2).reset_index()
print(mean_df)
criteria = ["review_scores_communication","review_scores_rating", "review_scores_cleanliness", "review_scores_checkin", "review_scores_location", "review_scores_value"]
trace = go.Heatmap(x = df['number_of_reviews'],
                   y = df['review_scores_rating'],
                   z = df['log10_price'],

                   colorscale = 'Viridis')

grouped = df.groupby('neighbourhood_group_cleansed').agg({'price': 'median', 'id': 'count'})
grouped.reset_index(inplace=True)
grouped.rename(columns={'id': 'listings_per_neighborhood', 'price': 'median_price'}, inplace=True)
room_type_counts = df.groupby(['room_type', 'neighbourhood_group_cleansed'])['id'].count().reset_index()
host_verified_counts = df.groupby(['host_identity_verified', 'neighbourhood_group_cleansed'])['id'].count().reset_index()
prop_type_counts = df.groupby(['property_type', 'neighbourhood_group_cleansed'])['id'].count().reset_index().sort_values(by="id", ascending=False).head(50)
fig_room = px.bar(room_type_counts, x='room_type', y='id', color='neighbourhood_group_cleansed', barmode='stack',
 labels={"id": "Properties Count",
 "room_type" : "Room Type", "neighbourhood_group_cleansed": "Neighbourhood"}, title = "Room type count")
host_verified = px.bar(host_verified_counts, x = "host_identity_verified", y= "id", color='neighbourhood_group_cleansed', barmode='stack', title =" Host Identity Verification")
host_superhost_count = df.groupby(['host_is_superhost', 'neighbourhood_group_cleansed'])['id'].count().reset_index()
host_superhost = px.bar(host_superhost_count, x = "host_is_superhost", y= "id", color='neighbourhood_group_cleansed', barmode='stack', title = "Superhosts")
instant_bookable_count = df.groupby(['instant_bookable', 'neighbourhood_group_cleansed'])['id'].count().reset_index()
instant_book = px.bar(instant_bookable_count, x = "instant_bookable", y= "id", color='neighbourhood_group_cleansed', barmode='stack', title ="Instant bookable property")
fig_room.update_layout(legend=dict(
    orientation="h",
    yanchor="bottom",
    y=1.02,
    xanchor="right",
    x=1
))
fig_room.update_xaxes(tickangle=45)

fig_prop = px.bar(prop_type_counts, x='property_type', y='id', color='neighbourhood_group_cleansed', barmode='stack',
 labels={"id": "Properties Count",
 "property_type" : "Property Type", "neighbourhood_group_cleansed": "Neighbourhood"}, title = "Properties type count")
fig_prop.update_layout(legend=dict(
    orientation="h",
    yanchor="bottom",
    y=1.02,
    xanchor="right",
    x=1
),xaxis={'categoryorder':'total descending'})
fig_prop.update_xaxes(tickangle=45)

parallel_plot = px.parallel_coordinates(df, color="log_price",
                              dimensions=["accommodates",'review_scores_rating', 'availability_365', "host_acceptance_rate"],
                              color_continuous_scale=px.colors.diverging.Tealrose,
                              title="Parallel plot of listings attributes")


figa = go.Figure()

for g in mean_df.index:
    figa.add_trace(go.Scatterpolar(
        r = mean_df.loc[g].values,
        theta = criteria,
        fill = 'toself',
        name = f'{mean_df["neighbourhood_group_cleansed"][g]}'
    ))

figa.update_layout(
  polar=dict(
    radialaxis=dict(
      visible=True,
      range=[0, 5] # here we can define the range
    )),
  showlegend=True,
    title="Average Customer Satisfaction by Neighborhood",
    title_x=0.5
)

verified_hosts = df[df['host_identity_verified'] == 'T']
neighborhood_counts = verified_hosts.groupby('neighbourhood_group_cleansed').count()['id']


layout = html.Div([
    html.H1(" "),
    html.H1(" "),

    dcc.RadioItems(
        id='price_type',
        options=options_price,
        value='price',
        labelStyle={'display': 'inline-block'}
    ),
    dcc.Graph(id='mapbox-scatter'),
    html.Div(className='row', children=[
        html.Div(className='col-4', children=[
            dcc.Graph(
                id='room-type-bar-chart',
                figure= fig_room
            ),]),
        html.Div(className='col-8', children=[
            dcc.Graph(
                id='prop-type-bar-chart',
                figure= fig_prop
            )


        ])
    ]),

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
    html.Label("Availability"),
    dcc.RadioItems(
        id='availability-select',
        options=[
            {'label': '30 days', 'value': 'availability_30'},
            {'label': '60 days', 'value': 'availability_60'},
            {'label': '90 days', 'value': 'availability_90'},
            {'label': '365 days', 'value': 'availability_365'}
        ],
        value='availability_30',
        labelStyle={'display': 'inline-block'}
    ),
    html.Label("Price"),
    dcc.RangeSlider(
            id="price_range",
            min=df["price"].min(),
            max=df["price"].max(),
            step=1,
            value=[df["price"].min(), df["price"].max()],
            marks={
                int(df["price"].min()): str(df["price"].min()),
                int(df["price"].max()): str(df["price"].max()),
            },
        ),
    dcc.Graph(id='scatter-plot'),
    dcc.Graph(
        id='reviews-heatmap',
        figure={
            'data': [trace],
            'layout': {
                'title': 'Relationship between Review Scores and Number of Reviews and Price',
                'xaxis': {'title': 'Number of Reviews'},
                'yaxis': {'title': 'Review Score'}
            }
        }
    ),
    html.Div(className='row', children=[
       
        html.Div(className='col-4', children=[
            dcc.Graph(
                figure= host_verified
            )]),
        html.Div(className='col-4', children=[
            dcc.Graph(
                figure = host_superhost
            )]),
        html.Div(className='col-4', children=[
            dcc.Graph(
                figure = instant_book
            )
        ])
        ]),


    html.Div(className='row', children=[
       
        html.Div(className='col-4', children=[
            dcc.Graph(
                id='customer_satisfaction',
                figure=figa
                )]),
        html.Div(className='col-8', children=[
            dcc.Graph(
                id='parallel-coordinates-plot',
                figure = parallel_plot

            )
        ])
        ]),
])
@callback(
    Output('scatter-plot', 'figure'),    
    [Input('availability-select', 'value'),
    Input("price_range", "value"),
    ]
)


def generate_scatter_plot(selected_availability, price_range):
    filtered_df = df[
        (df["price"] >= price_range[0]) &
        (df["price"] <= price_range[1])
    ]

    fig = px.scatter(filtered_df, x=selected_availability, y='price', color='neighbourhood_group_cleansed',
                    hover_data=['neighbourhood'], labels={"neighbourhood_group_cleansed": "Neighbourhood"},
                    title = "Relationship between price and availability")
    return fig

def update_scatter_plot(selected_availability, price_range):
    return generate_scatter_plot(selected_availability, price_range)
@callback(
    Output("mapbox-scatter", "figure"),
    Input("price_type", "value"))
def generate_graph(price_type):
    if price_type == 'price':
        p = 'price'
        map_fig = px.scatter_mapbox(df, lat='latitude', lon='longitude', text='name',
                        color='neighbourhood_group_cleansed',
                        size=p, size_max=60,
                        color_discrete_sequence=px.colors.qualitative.G10,
                        zoom=10, height=550, hover_data=['price', 'property_type'])
        map_fig.update_layout(mapbox_style="open-street-map", legend=dict(
            y=1.02,
            xanchor="left",
            x=1
        ),margin={"r":0,"t":10, "l":0,"b":0})
    elif price_type == "density":
        grouped = df.groupby(['latitude', "longitude"]).size().reset_index(name='listings_count')
        print(grouped.head())
        map_fig = px.density_mapbox(grouped, lat='latitude', lon='longitude', z=grouped['listings_count'],
                    color_continuous_scale="Viridis", mapbox_style="carto-positron",
                    zoom=10, height=550)
        map_fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

    else:
        p = 'log_price'
        df_temp = df[df["log_price"] >0]
        map_fig = px.scatter_mapbox(df_temp, lat='latitude', lon='longitude', color='log_price',
                 hover_name='property_type',
                 hover_data=['price', 'property_type'],
                 color_continuous_scale=px.colors.sequential.Plasma)


        map_fig.update_layout(mapbox_style="open-street-map", legend=dict(y=1.02,xanchor="left",x=1))
        map_fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

    return map_fig

def update_plot(price_type):
    return generate_graph(price_type)