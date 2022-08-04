# Import necessary libraries 
from dash import html
import dash_bootstrap_components as dbc
from pages import navigate

center_c = "h-100 d-flex align-items-space-around justify-content-center m-5"

skip = navigate.nav('home','skip')
next_arrow = navigate.nav('future','next')
back = navigate.nav('basic_explanation','back')

layout = html.Div([
    dbc.Container([
        skip,
        html.H1(f'Technical Stuff',style={'color':"#112a42"},className='text-center mt-5 mb-10'),
        back,
                    ]),
    
    html.H2('*',className=center_c),
    html.H3("Aligned with Up&Up's tech vision",className=center_c),
    html.H5("Clean framework made of clean building blocks.",className=center_c),
    html.P('Clear workflow and documentation is easy to follow and easy to fix.',className=center_c),
    html.P('Attention to detail with feature engineering. Ex. Diversity Index measure using KL Divergence.',className=center_c),
    html.H5("Easily adaptable building blocks.",className=center_c),
    html.P('Ex. Weight input for similarity function takes a simple dictionary of features and weights.',className=center_c),
    html.P('Dictionary values could also be functions/transformations for more complicated weighting models.',className=center_c),
    html.H5("Scalable with changing team and customer needs.",className=center_c),
    html.P('Data features can be easily added and engineered.',className=center_c),
    html.P('Additional features or newly engineered features only need to be added in 2-3 key lists after being merged.',className=center_c),
    html.H5("Everything from data pulling, cleaning, to model building is flexible, and built for improvement.",className=center_c),
    html.P('Can pull basic data for any new area. Data pulling for schools and amenities are seperate but processes for pulling and storing those will be documented.',className=center_c),
    html.H3("Technical Specifics",className=center_c),
    html.A(html.H5("Model Building Notebook",className=center_c),href='https://64c23e0c644748ce-dot-us-east4.notebooks.googleusercontent.com/lab/workspaces/auto-8/tree/mehika_nbhd_similarity/3_milestone_cenuss%2Bamenities_data.ipynb'),
    html.A('Docs here.', href='https://www.notion.so/upandup/Neighborhood-Similarity-Model-Documentation-facd3130e47b40d7ab97a00b9e218a5c',className=center_c),
    
    
    html.Div(next_arrow,className=center_c)
    
    
])