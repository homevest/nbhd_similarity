# Import necessary libraries 
from dash import html
import dash_bootstrap_components as dbc
from pages import navigate
import plotly.express as px
import pandas as pd

#formatting & arrows
center_c = "h-100 d-flex align-items-space-around justify-content-center m-5"
w = '500px'
skip = navigate.nav('home','skip')
next_arrow = navigate.nav('weights_explanation','next')
back_arrow = navigate.nav('context','back')

#plotting stuff for math explanation

df = pd.read_csv('math.csv')
df.rename(columns={'sepal_length':'Population Density',
                  'sepal_width':'Average School Rating',
                  'petal_width':'Parks per 10k sqft'},inplace=True)

# fig = px.scatter_3d(df, x='Population Density', y='Average School Rating', z='Parks per 10k sqft',
#             color='Nbhd', 
#               symbol='Nbhd', opacity=0.7)

## tight layout
# fig.update_layout(showlegend=False,
#                  coloraxis_showscale=False,
#                  margin=dict(l=0, r=0, b=0, t=0))
# fig.write_html('math.html')

#WITH LINES
# Define the page layout


# fig = px.scatter_3d(df, x='Population Density', y='Average School Rating', z='Parks per 10k sqft',
#             color='Nbhd', 
#               symbol='Nbhd', opacity=0.7)

# fig.add_trace(px.line_3d(df,x='Population Density', y='Average School Rating', z='Parks per 10k sqft').data[0])

# fig.update_layout(showlegend=False,
#                  coloraxis_showscale=False,
#                  margin=dict(l=0, r=0, b=0, t=0))
# fig.write_html('math_with_lines.html')


layout = html.Div([
    dbc.Container([
        back_arrow,
        skip,
        html.H1('Measuring Similarity',style={'color':"#112a42"},className='text-center mt-5 mb-10'),
                    ]),
    
    html.H5('*',className=center_c),
    html.H4('Similarity Measured by least difference among area attributes',className=center_c),
    html.Ul([
        html.H5('Commonly Acknowledged Neighborhood Attributes',className='border mt-5 mb-2'),
        html.Img(src='assets/img/key.svg',width='60px'),'Safety',
        html.Img(src='assets/img/schoolhouse.svg',width='60px'),'Schools',
        html.Img(src='assets/img/city.svg',width='60px'),'City Life',
        html.Img(src='assets/img/amenities.svg',width='60px'),'Amenities',
        html.Img(src='assets/img/tree.svg',width='60px'),'Greenery',
        html.Img(src='assets/img/people.svg',width='60px'),'Demographics',
        html.Img(src='assets/img/growth.svg',width='75px',height='50px'),'Area Growth Potential',
        html.P('Neighborhoods with the least difference among attributes are the most similar.',className=center_c),
        ],
        style = {'list-style':'none'},
        className=f'list-group {center_c} align-items-center rounded border pt-2'
    ),

    
    html.P('Areas with similarly rated schools, similar population density, crime levels, demographics, etc. are likely to be similar neighborhoods.',className=center_c),
    
    html.H4('Feature Difference = Numerical Distance between features',className=center_c),
    
    html.H6('Minkowski Distance',className=center_c),
    
    html.Div(html.Img(src="assets/img/minkowski.png",width='250px'),className=center_c),
    
    
    html.Div([html.Iframe(id='math-plot', srcDoc = open('math_with_lines.html','r').read(),width='50%',height='500')],className=center_c),

    
    html.Div(next_arrow,className=center_c)
    
])
