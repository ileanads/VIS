from dash import html
import dash
from PIL import Image

pil_image = Image.open('nyc.jpg')# replace with your own image

layout = html.Div(children=[
    html.Img(src = pil_image, style={'width': '100%'})

])