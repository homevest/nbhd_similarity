#import packages

#basics
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import mapclassify
import copy

#stats
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler
from scipy.special import rel_entr
from statsmodels.stats.outliers_influence import variance_inflation_factor
from statsmodels.tools.tools import add_constant
from sklearn.linear_model import RidgeCV, LassoCV,ElasticNetCV
from sklearn.linear_model import Ridge, Lasso, ElasticNet
from sklearn.metrics import mean_squared_error,r2_score
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn import model_selection
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import MinMaxScaler

#spatial
import geopandas as gpd
from shapely.geometry import Point
from shapely import wkt


#plotting
import matplotlib.pyplot as plt
import plotly.express as px #if using plotly

#data
import censusdata
import us
from us import states
from google.cloud import bigquery, storage
client = bigquery.Client(location="US")

FINAL_FEATURES = ['population_density', 
                'median_age',
                'median_hh_income',
                'median_home_value',
                'income_gini',
                'diversity_index',
                'percent_bachelor_degree',
                'percent_high_school_graduate',
                'percent_homes_occupied_by_owner',
                'percent_homes_occupied_by_renter',
                '10_y_population_%_change',
                '10_y_median_home_value_%_change',
                '10_y_income_gini_%_change',
                '10_y_diversity_index_%_change',
                '10_y_percent_homes_occupied_by_owner_%_change',
                '10_y_percent_homes_occupied_by_renter_%_change',
                '5_y_population_%_change', 
                '5_y_median_home_value_%_change',
                '5_y_income_gini_%_change',
                '5_y_diversity_index_%_change',
                '5_y_percent_homes_occupied_by_owner_%_change',
                '5_y_percent_homes_occupied_by_renter_%_change',
                # 'STATEFP', 'COUNTYFP','GEOID', 'NAME', 'MTFCC', 'FUNCSTAT', 'ALAND', 'AWATER', 'lat', 'lng', 'geometry', '100000_sqft', 'enrollment', 'numReviews', 
                'school_rating',
                # 'city_life_rating', 
                # 'city_life_density', 
                'cultural_rating',
                'cultural_density',
                'greenery_rating',
                'greenery_density',
                'retail_rating',
                'retail_density',
                'negative_density',
                'restaurants_rating',
                'restaurants_density',
                'nightlife_rating',
                'nightlife_density',
                'fitness_rating',
                'fitness_density']

def noncollinear_features_VIF(data):
    ''' This function uses VIF (Variance Inflation Factor),or other methods to find collinear features within a provided dataset, and returns the subset of features that are not collinear. '''
    selected_features = copy.deepcopy(FINAL_FEATURES)
    highest_vif = compute_vif(data,FINAL_FEATURES).sort_values(by='VIF', ascending=False).iloc[0].VIF
    
    while highest_vif>5:
        #remove highest VIF variable from selected_features list
        selected_features.remove(compute_vif(data,selected_features).sort_values(by='VIF', ascending=False).iloc[0].Variable)
        #recalculate highest VIF
        highest_vif = compute_vif(data,selected_features).sort_values(by='VIF', ascending=False).iloc[0].VIF 
    return selected_features

# Computes the vif for all given features
def compute_vif(data,considered_features):
    X = data[considered_features]
    # the calculation of variance inflation requires a constant
    X['intercept'] = 1
    # create dataframe to store vif values
    vif = pd.DataFrame()
    vif["Variable"] = X.columns
    vif["VIF"] = [variance_inflation_factor(X.values, i) for i in range(X.shape[1])]
    vif = vif[vif['Variable']!='intercept']
    return vif

def run_rr(data,optimize_column):
    ''' Pulls weights optimized for a certain feature. This is based on the assumption that a multilinear regression model fit on a certain variable will produce feature coefficients indicative of magnitude of importance to that optimization variable.
    This can be run on the entire dataset, or on subsets of a dataset. Weights can be tuned specific to market, to all markets, or to specific subsets within a market. Reasons for this can vary. One reason to optimize on a subset of a market is to 
    identify a subset of a market that has seen significant growth, and wanting only to consider those areas instead of the whole market. '''
    
# Could also run nonlinear/polynomial models to find weights (weights would be functions rather than simple numeric values in this case, where f(x) would transform the given feature x and be the new input for the nearest neighbors comparison.

    data = copy.deepcopy(data[FINAL_FEATURES])
    
    # Pull X & Y
    y = data[optimize_column]
    X = data.drop(columns=optimize_column)

    # Standardize all features
    scaler = StandardScaler()
    X = scaler.fit_transform(X)

    # fit model 
    model = ElasticNetCV(
            cv=10,
            l1_ratio=[.1, .5, .7, .9, .95, .99, 1])
    model.fit(X,y)

    print(f'Model Score: {model.score(X,y)}')
    
    x_cols = list(data.drop(columns=optimize_column).columns)
    
    return make_dict(x_cols,np.abs(model.coef_))


def make_dict(keys,values):
    final_dict = {}
    for k in range(len(keys)):
        final_dict[keys[k]] = values[k]
    return final_dict
        
# Default weights, groupings, and ranked list! 
FEATURE_GROUPS = {
    
    'density':['population_density','retail_density'],
    'negative':['negative_density'],
    'demographics':['percent_homes_occupied_by_owner','percent_homes_occupied_by_renter',
                   'percent_bachelor_degree','income_gini',
                   'diversity_index','median_hh_income','median_home_value',
                   'median_age'],
    'schools':['school_rating','cultural_rating','cultural_density','percent_high_school_graduate'],
    'city_life':['restaurants_rating','restaurants_density',
                 'nightlife_rating','nightlife_density','retail_rating'],
    'greenery_fitness':['greenery_rating','greenery_density',
                        'fitness_rating','fitness_density'],
    'area_growth':['10_y_population_%_change','10_y_median_home_value_%_change','10_y_income_gini_%_change',
                  '10_y_diversity_index_%_change','10_y_percent_homes_occupied_by_owner_%_change','10_y_percent_homes_occupied_by_renter_%_change',
                  '5_y_population_%_change','5_y_median_home_value_%_change','5_y_income_gini_%_change',
                  '5_y_diversity_index_%_change','5_y_percent_homes_occupied_by_owner_%_change','5_y_percent_homes_occupied_by_renter_%_change'],
}

DEFAULT_GROUP_WEIGHTING = { 0: .3,
                            1: .225,
                            2: .15,
                            3: .125,
                            4: .1,
                            5: .075,
                            6: .025,
                            }

DEFAULT_RANKED_LIST = ['schools','greenery_fitness','demographics',
                  'area_growth','density','city_life','negative']



# Function that takes a ranked list of groups, rank weights, and feature groups
# that show what features are in each grouping

def assign_weights_to_groups(ranked_groups  = DEFAULT_RANKED_LIST,
                             rank_weights   = DEFAULT_GROUP_WEIGHTING,
                             feature_groups = FEATURE_GROUPS):
    group_weights = {}
    feature_weights = {}
    
    # assign weights to feature groups
    for i in range(len(rank_weights)):
        group_weights[ranked_groups[i]] = rank_weights[i]
    
    # distribute weights assigned to each group between all features in feature group
    for k,v in group_weights.items():
        for feature in feature_groups[k]:
            feature_weights[feature] = group_weights[k] / len(feature_groups[k])

    return feature_weights

def nearest_neighbors(data,selected_tract, algorithm='brute', weights=False, weights_optimized_for =False, n=10):
    idx_selected = data.reset_index()[data.index == selected_tract].index #find index of selected tract
    
    print(f'Finding Most Similar Neighborhoods to {selected_tract}...')
    
    X = copy.deepcopy(data[FINAL_FEATURES])
    

    # Apply weights
    if weights: # Multiply columns by weights if provided
        X = multiply_features_by_weights(X, weights)
    else:
            #remove collinear vars
        X = X[noncollinear_features_VIF(X)]
        # Standardize data
        X = pd.DataFrame(StandardScaler().fit_transform(X))
   

    nbrs = NearestNeighbors(n_neighbors=n, algorithm = algorithm).fit(X)
    distances, indices = nbrs.kneighbors(X)
    # data[f'distance_from_{selected_tract}'] = distances
    # show nearest neighbors 
    return data.iloc[indices[idx_selected.values[0]]]

def multiply_features_by_weights(features,weights):
    features = features[weights.keys()] # remove any unweighed variables (e.i. the one optimized for)
    # Standardize data
    features = pd.DataFrame(StandardScaler().fit_transform(features),columns=features.columns)
    for k in weights.keys():
        features[k] = features[k] * weights[k]
    return features

        

        