# Dash imports
import dash
from dash import html, dash_table, dcc, callback
from dash.dependencies import Input, Output
from dash.dependencies import State
import dash_bootstrap_components as dbc
import plotly.express as px
import folium
import navbar

# Data & NBHD imports
import censusdata
from us import states 
from nbhd_similarity import *
from data_preparing import *

center_c = "h-100 d-flex align-items-space-around justify-content-center"


nav = navbar.Navbar()

# App layout
layout = html.Div([
    dbc.Row([nav]),
    # Store component 
    dcc.Store(id='local', storage_type='local'),
    
    # Form section
    dbc.Container([
        html.H1("Neighborhood Similarity",
                         className='text-center text-primary mt-5 mb-5'),
        dbc.Row([
                dbc.Col([html.H5("Select a Market.", className='mt-4'),   
                         html.Div([dcc.Dropdown(
                                    options = [{'label': 'Atlanta', 'value': 'atl'},
                                               {'label': 'St. Louis', 'value': 'stl'},
                                               {'label': 'Indianapolis', 'value': 'indy'},
                                               {'label': 'Greenville', 'value': 'gvil'},
                                               {'label': 'New York City', 'value': 'nyc'},
                                               {'label': 'Greensboro', 'value': 'gboro','disabled': True},
                                               {'label': 'Birmingham', 'value': 'birmingham','disabled': True},
                                               {'label': 'Cincinatti', 'value': 'cincinatti','disabled': True},
                                              ],
                                    placeholder='Select Market',
                                    persistence=True,
                                    persistence_type='memory',
                                id='market',

                            )],id='market-selection'),

                         html.Div([],id='census-tracts'),],style={'width':'50%'}),

                dbc.Col([
                        html.Div([],id='weight-options-form'),
                        ],style={'width':'50%',
                                 'display':'flex',
                                 'flex-direction':'column',
                                 'justify-content':'align-center'},
           
                
                ),
            ]),
        html.Div([],id='similar-neighborhoods-table'),
                        html.Br(),
                        html.Div([],id='similar-neighborhoods-map'),
        
    ],
    ),
])

@callback(
    Output('census-tracts','children'),
    Output('weight-options-form','children'),
    Input('market','value')
)
def show_map_and_tract_options(market):
    df = csv_to_geodataframe(f'data/df_{market}.csv')
    m = folium.Map(location=[(df.lat.median()),(df.lng.median())]) 
    df.explore(color='blue',
                tooltip='tract',m=m)
    (m).save('market_map.html')
    return (html.Div([
        dcc.Dropdown(
                options = list(df.index),
                placeholder='Select A Neighborhood!',
                persistence=True,
                persistence_type='memory'
            ,
            id='census-tract',
            # style={'width':'50%'}
            ),
        html.Iframe(id='map', srcDoc = open('market_map.html','r').read(),width='100%',height='600'),
        # dcc.Dropdown(options = FINAL_FEATURES,
        #                 id = 'optimization-variable',
        #                 multi=False,
        #                 value=FINAL_FEATURES[0])
        #     ],id='optimizing-div',
        #       style=opt_style,
        #       className='m2'
        #      ),
    ]),
        [
        html.H5('How would you like to conduct your search?',className=f'text-center m-4'),
        dbc.RadioItems(
            options=[
                       {'label': 'Optimize for a Feature', 'value': 'optimize'},
                       {'label': 'Rank Features Myself', 'value': 'rank'},
                        {'label': 'Weight All Features Equally', 'value': 'no_weights'},
                    ],
            persistence=True,
            persistence_type='memory',
            id='weight-options-radio',
            # style={'width':'50%'}
),
        html.Div([],id='rank-or-optimize-options'),
        
        ])



@callback(
    Output('rank-or-optimize-options','children'),
    Input('weight-options-radio','value'),
)

def rank_or_optimize_options(selected_weight_option):
    # set up hiding div for other option if one option is selected with css style
    opt_style = {'display':'none'}
    rank_style = {'display':'none'}
    btn_style = {'display':'none'} #block is default display style
    
    if selected_weight_option=='no_weights':
        btn_style = {'display':'block'}
        
    elif selected_weight_option == 'optimize':
        opt_style = {'display':'block'}
        btn_style = {'display':'block'}
        
    elif selected_weight_option == 'rank':
        rank_style = {'display':'block'}
        btn_style = {'display':'block'}
    
    
    return html.Div([
                    html.Div([
                        html.H5('Select a feature to optimize for.',className=f'{center_c} m-5'),
                        dcc.Dropdown(options = FINAL_FEATURES,
                                        id = 'optimization-variable',
                                        multi=False,
                                        value=FINAL_FEATURES[0])
                            ],id='optimizing-div',
                              style=opt_style,
                              className='m2'
                             ),
        
                    html.Div([
                        html.H5('Select Features in Order of Importance. All features must be selected to run.', className='text-center m-5'),
                        dcc.Dropdown(options = list(FEATURE_GROUPS.keys()),
                                        id = 'ranked-list',
                                        multi=True,
                                        value=list(FEATURE_GROUPS.keys())[0])
                            ],id='ranking-div',
                              style=rank_style,
                              className='m2'),
                    html.Div([html.Button('Find Neighborhoods',id='run-nn', n_clicks=0,className="btn btn-outline-primary",style = btn_style)], className=f'{center_c} m-5', style = btn_style)
                    ])


@callback(
    Output('similar-neighborhoods-table','children'),
    Output('similar-neighborhoods-map','children'),
    Input('run-nn','n_clicks'),
    State('census-tract','value'),
    State('market','value'),
    State('weight-options-radio','value'),
    State('optimization-variable','value'),
    State('ranked-list','value'),
)
def run_nn(n,tract,market,weight_source,optimization_column,ranked_list):
    if n > 0:
        df = csv_to_geodataframe(f'data/df_{market}.csv')

        if weight_source == 'rank':
            weights = assign_weights_to_groups(
                                 ranked_groups  = ranked_list,
                                 rank_weights   = DEFAULT_GROUP_WEIGHTING,
                                 feature_groups = FEATURE_GROUPS)
        elif weight_source == 'optimize':
            weights = run_rr(df, optimization_column)

        else:
            weights = False

        nn = nearest_neighbors(df,tract, weights = weights, n=8)
        print(nn)
        m = folium.Map(location=[(nn.lat.median()),(nn.lng.median())]) 
        
        nn.explore(color='blue', tooltip=['tract'], m=m)
        
        nn.iloc[0:1].explore(color='green', tooltip='tract', m=m)
        
        (m).save('similar_neighbors_map.html')
        
        nn = pd.DataFrame(nn).drop(columns=["STATEFP","COUNTYFP","GEOID","NAME","MTFCC","FUNCSTAT","ALAND","AWATER","lat","lng","geometry"]).reset_index().style.set_table_styles([
                                                                    {"selector": "td,th", "props": "white-space:nowrap; padding: 1px; border: 1px solid black;"}                         
                                                                   ])
        nn.to_html('table.html')
        return [html.Iframe(id='table',srcDoc = open('table.html','r').read(),width='100%',height='200px')],[html.Iframe(id='map',srcDoc = open('similar_neighbors_map.html','r').read(), width='100%',height='600')]
    
    
if __name__ == '__main__':
    app.run_server(debug=True, host="0.0.0.0", port=8000)
