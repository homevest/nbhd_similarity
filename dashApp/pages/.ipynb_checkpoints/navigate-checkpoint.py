# Import necessary libraries
from dash import html
import dash_bootstrap_components as dbc

def nav(page='home',direction='skip'):
    if direction=='skip':
        style_css = {'position':'absolute',
                 'top':'5px','right':'5px'}
        img = 'assets/img/skip_arrow.png'
        h = "40x"
        c ='mt-4 mb-4'
        
    elif direction=='next':
        style_css = {}
        img = 'assets/img/right_arrow.png'
        h = "60px"
        c=''
    else:
    # elif direction=='back':
        style_css = {'position':'absolute',
                 'top':'5px','left':'5px'}
        img = 'assets/img/left_arrow.png'
        h = "40x"
        c='mt-4 mb-4'
    nav = html.Div([dbc.Nav(
        children=[
     dbc.NavItem(dbc.NavLink(html.Img(src=img, height=h, title="Skip Walkthrough"), href=f"/{page}")),
        ],
        
    )],className=c,
       style = style_css)
    
    return nav
