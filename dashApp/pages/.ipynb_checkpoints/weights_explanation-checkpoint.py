# Import necessary libraries 
from dash import html
import dash_bootstrap_components as dbc
from pages import navigate

center_c = "h-100 d-flex align-items-space-around justify-content-center m-5"

skip = navigate.nav('home','skip')
next_arrow = navigate.nav('home','next')
back = navigate.nav('basic_explanation','back')

layout = html.Div([
    dbc.Container([
        skip,
        html.H1(f'Flexible to match use case',style={'color':"#112a42"},className='text-center mt-5 mb-10'),
        back,
                    ]),
    
    html.H3(f'Each neighborhood attribute is not equally important',className=center_c),
    html.Div([html.Img(src='assets/img/scale.svg',width='25%'),
              
    html.Div([
    html.H5("Our team's priorities change."),
    html.P("Our acquisitions team could be searching for the next Williamsburg, or to simply find neighborhoods similar to those in our portfolio that have seen high value growth."),
    
    html.H5('Not all customers have the same priorities.'),
    html.P('A family with kids might care more for a neighborhood with great schools similar to a given neighborhood, while a young couple might care for a similar density of night-life amenities.'),
    
    ],style={'width':'35%','justify-content':'space-between'}),
             ],
              
              className=center_c),
    html.P('This model accounts for these contextual differences when measuring neighborhood similarity by weighting features according to context.',className=center_c),
    html.H3(f'2 Methods for Feature Weighting',className=center_c),
    html.H5('1. User Ranks Feature Groups According to their priorities',className=center_c),
    html.H5('2. Model finds how valuable each feature is to a selected variable',className=center_c),
    
    html.H6('Elastic Net',className=center_c),
    html.Div(html.Img(src="assets/img/elastic_net.png",width='500px'),className=center_c),
    
    
    html.Div(next_arrow,className=center_c)
    
])
