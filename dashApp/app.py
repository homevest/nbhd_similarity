# Dash imports
import dash
from dash import html, dash_table, dcc
from dash.dependencies import Input, Output
from dash.dependencies import State
import dash_bootstrap_components as dbc
import plotly.express as px
import folium

# Data & NBHD imports
import censusdata
from us import states
from nbhd_similarity import *
from data_preparing import *

# Pages
from pages import home, title,context, basic_explanation,weights_explanation,technical_stuff,future

dbc_css = 'assets/bootstrap.css'
external_stylesheets = [dbc.themes.LUX, dbc_css,                       'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css'
]


app = dash.Dash(__name__,
            external_stylesheets = external_stylesheets
                ,suppress_callback_exceptions=True
                )
app.config.suppress_callback_exceptions=True

# dash.register_page("home", layout="We're home!", path="/")


app.layout = html.Div([
    dcc.Location(id='url',refresh=False),
    html.Div([],id='page-content')
    # dash.page_container,
])

@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/' or  pathname == '/title':
        return title.layout
    if pathname == '/context':
        return context.layout
    if pathname == '/basic_explanation':
        return basic_explanation.layout
    if pathname == '/weights_explanation':
        return weights_explanation.layout
    if pathname == '/technical_stuff':
        return technical_stuff.layout
    if pathname == '/future':
        return future.layout
    if pathname == '/home':
        return home.layout
    else: # if redirected to unknown link
        return ["404 Page Error! Redirected to home.",home.layout]



if __name__ == '__main__':
    app.run_server("0.0.0.0", port=80)
