#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 29 22:53:05 2025

@author: laurendonnelly
"""

from data_and_funcs import export_data 

from dash import Dash, html, dcc, callback, Output, Input, State, ctx, no_update
from plotly.graph_objects import Figure
import plotly.express as px
import pandas as pd
#%%
data, units_dict = export_data()

#%% columns of interest, data with reset indices

df = data.reset_index()
cols_options = data.columns
#%% other variables for dash application
sources = ["FAOSTAT production, employment, population and macroeconomics data; https://www.fao.org/faostat/en/#data", "Our World in Data land area data; https://ourworldindata.org/grapher/land-area-hectares"]
sources_html_component = html.Ul([html.Li(item) for item in sources])

variables_expl = ["Yield — in kg/ha, describes the annual yield of rice in the selected country",
                  "Urban:Rural — a ratio, describes the ratio of urban to rural",
                  "total_population — in thousands, the population of the country",
                  "employed_in_ag – in thousands, the total number of workers employed in the agricultural sector",
                  "percent_employed_in_ag — percentage, the proportion of the total population employed in agriculture",
                  "val_added_percent_GDP — percentage, the value added by the Agriculture, Forestry and Fishing sector as a percent of the country's GDP",
                  "val_added_mil_USD — mil USD, the value added by the Agriculture, Forestry and Fishing sector in the country in millions of USD"]
variables_html_component = html.Ul([html.Li(item) for item in variables_expl])

#%%

app = Dash(__name__)
server = app.server

app.layout = html.Div([
    html.H1(children="Exploration of rice agricultural trends in selected countries",style={'textAlign': 'center'}),
    
    dcc.Dropdown(cols_options,cols_options[0],id='dropdown-selection'),
    
    dcc.Graph(id='single-var-time-gr'),
    
    html.H3(children="Sources"),
    sources_html_component,
    
    html.H3(children="Variables explanation"),
    variables_html_component
    ])

@callback(
    Output('single-var-time-gr','figure'),
    Input('dropdown-selection', 'value')
    )

def update_graph(value):
    fig = px.line(df, x='Year', y=value,title=f"{value} by Country", color="Area")
    
    return fig


if __name__ == '__main__':
    app.run(debug=True)
    