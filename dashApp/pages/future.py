# Import necessary libraries 
from dash import html
import dash_bootstrap_components as dbc
from pages import navigate

center_c = "h-100 d-flex align-items-space-around justify-content-center m-5"

skip = navigate.nav('home','skip')
back = navigate.nav('technical_stuff','back')

layout = html.Div([
    dbc.Container([
        skip,
        html.H1(f'The Future',style={'color':"#112a42"},className='text-center mt-5 mb-10'),
        back,
                    ]),
    html.H2('*',className=center_c),
    html.H4('General Learnings for the future',className=center_c),
    html.P('Opportunity to improve our data collection, nomenclature, and documentation process',className=center_c),
    html.P('Adding Quota Limits on priced APIs or implementing a function to calculate costs before pulling data',className=center_c),
    html.P('Collection of API keys (i.e. free yelp keys: I have 4!)',className=center_c),
    html.H4('Data Possibilities',className=center_c),
    html.P('More indepth analysis of high growth neighborhood & targetting unexpected areas for investment.',className=center_c),
    html.P('Climate comparison between neighborhoods using Google Earth Engine',className=center_c),
    html.P('Nuance amenities categories. Ex. # Fast food restaurants vs High-end restaurants',className=center_c),
    html.H4('Model and Implementation Possibilities',className=center_c),
    html.P('Optimization function to find weights can use models beyond penalized regression',className=center_c),
    html.P('For Grouped feature weighting: fine tuning distribution of a weight assigned to a feature group',className=center_c),
    html.P('Add ranking features ability to search system on Up&Up website.',className=center_c),
    html.P('Cross-market comparison.',className=center_c),
   
])

