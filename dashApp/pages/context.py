# Import necessary libraries 
from dash import html
import dash_bootstrap_components as dbc
from pages import navigate

center_c = "h-100 d-flex align-items-space-around justify-content-center m-5"
w = '500px'

skip = navigate.nav('home','skip')
next_arrow = navigate.nav('basic_explanation','next')



# Define the page layout
layout = html.Div([
    dbc.Container([
        skip,
        html.H1('Model Business & Problem Context',style={'color':"#112a42"},className='text-center mt-5 mb-10'),
                    ]),
    
    html.H5('*',className=center_c),
    html.H3('Problem Context', className=center_c),
    html.H5('Find Neighborhoods Similar to Ones We Love',className=center_c),
    html.Img(src='assets/img/nbhds.svg'),

    # html.H5('*',className=center_c),

    html.H5('*',className=center_c),
    html.H3('Business Impact',className=center_c),
    html.Div(html.Img(src='assets/img/best_nbhd.svg',width='100px'),className="h-100 d-flex align-items-space-around justify-content-center"),
    html.H5('Invest in the best neighborhoods',className=center_c),
    html.Div(html.Img(src='assets/img/search.svg',width='100px'),className="h-100 d-flex align-items-space-around justify-content-center"),
    html.H5('Enhance customer experience with personalized area search',className=center_c),
    
    
    html.H5('*',className=center_c),
    html.H3('Key Questions',className=center_c),
    html.H5('-What defines a neighborhood?',className=center_c),
    html.H5('-What makes two neighborhoods similar?',className=center_c),
                   
    html.Div(next_arrow,className=center_c)
    
                   
])
