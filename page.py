from dash import html
import dash_bootstrap_components as dbc
from dash import dcc
import pandas as pd
from components.data_input import editable_input_table
from components.data_table import table
from components.slider import slide
from components.navbar import logo
import dash_leaflet as dl
import dash_leaflet.express as dlx

def bool_to_str(df):
    """Convert boolean column to string column
    due to Dash DataTable inability to display booleans"""
    for col, dtype in df.dtypes.items():
        if dtype == 'bool':
            df[col] = df[col].astype('str')
    return df

def html_page(res):
    df = pd.read_csv("centres.csv")

    test = df[['lat', 'lon']]
    markers = test.to_dict('record')
    markers = dlx.dicts_to_geojson(markers)

    editable_input = editable_input_table(bool_to_str(df))

    datatable = table(res)

    slider = slide()

    tab_style = {
        'padding': '6px',
        'border-radius': '10px',
        'background-color': '#FFFFFF',
        'box-shadow': '5px 5px 20px #ccc',
    }

    page = html.Div([
        dbc.Row([
            html.Div(logo, style={'padding': 40}),
            dbc.Row([
                dbc.Row(html.Div(editable_input)),
                dbc.Row(html.Br()),
            ]),
        ]),
        dbc.Row([
            dbc.Row(html.Div(datatable), style={'padding': 20}),
            dbc.Row(html.Br())
        ]),

        dbc.Row([
            dbc.Col(
                html.Label(id="slider-output"),
                width={"size": 3, "order": "last", "offset": 6}),
        ]),
        dbc.Row([
            dbc.Col(
                html.Div(slider),
                width={"size": 6, "order": "last", "offset": 3}),
        ]),
        dbc.Row([
            dbc.Col(html.Div(html.Div(dcc.Graph(id="bar-chart", style={'margin': 5})),
                             style=tab_style)),
            # dbc.Col(html.Div(html.Div(dcc.Graph(id="line-chart"),))),
            dbc.Col(html.Div([dl.Map(zoom=7, center=(df.lat.iat[0], df.lon.iat[0]),
                                     children=[dl.TileLayer(maxZoom=20),
                                               dl.GeoJSON(data=markers)])],
                             style={'width': '100%', 'height': '465px', 'margin': "auto", "display": "block",
                                    "position": "relative", 'backgroundColor': '#FF0000', 'border-radius': '8px',})),
            dbc.Col(html.Div(html.Div(dcc.Graph(id="pie-chart", style={'margin': 5})),
                             style=tab_style))
        ])
    ])
    return page
