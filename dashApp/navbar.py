# Import necessary libraries
from dash import html
import dash_bootstrap_components as dbc

# Define the navbar structure
def Navbar():

    layout = html.Div([
        dbc.NavbarSimple(
            children=[
                dbc.NavItem(dbc.NavLink("Business Context", href="/context")),
                dbc.NavItem(dbc.NavLink("Measuring Similarity", href="/basic_explanation")),
                dbc.NavItem(dbc.NavLink("Contextual Similarity", href="/weights_explanation")),
                dbc.NavItem(dbc.NavLink("Technical Stuff", href="/technical_stuff")),
                dbc.NavItem(dbc.NavLink("Future", href="/future")),
            ] ,
            brand="Walkthrough",
            brand_href="/title",
            color="#112a42",
            dark=True,
            style = {'width':'100%'}
        ), 
    ])

    return layout

