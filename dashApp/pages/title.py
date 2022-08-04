# Import necessary libraries 
from dash import html
import dash_bootstrap_components as dbc
from pages import navigate

center_c = "h-100 d-flex align-items-space-around justify-content-center m-20"
w = '500px'

skip = navigate.nav('home','skip')
next_arrow = navigate.nav('context','next')


# Define the page layout
layout = html.Div([
    dbc.Container([
        html.H1('Presentation: Neighborhood Similarity Tool + Methodology',style={'color':"#112a42"},className='text-center mt-5 mb-10'),
                    ]),
    
    html.H3('By Mehika P.',style={'color':"#112a42",'padding':'15%'},className='text-center mt-5 mb-10'),
    

    html.Div(next_arrow,className=center_c)
    
                   
])
