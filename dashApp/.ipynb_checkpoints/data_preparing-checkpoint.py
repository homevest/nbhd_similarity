#import packages

#basics
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
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


def state_fips(state): #pulls state fips
    return states.lookup(state).fips

def bq_to_df(query):
    query_job = client.query(
        query,
        location="US")
    df = query_job.to_dataframe()
    return df

def pull_census_tract_geodata(state,year=2020):
    file = gpd.read_file(f"https://www2.census.gov/geo/tiger/TIGER2020/TRACT/tl_2020_{states.lookup(state).fips}_tract.zip")
    return file

def cbsa_fips_code(state,county): #pulls all census tracts in county or entire state
    q = f"""
    SELECT cbsa_fips_code
    FROM `bigquery-public-data.geo_us_boundaries.counties` 
    WHERE geo_id = '{str(state_fips(state)) + str(county)}'
    
    """
    return bq_to_df(q).iloc[0].cbsa_fips_code


census_features = {
     'B02001_001E':'total_population'  # population amnt
    ,'B06011_001E':'median_hh_income'  # median_income
    ,'B01002_001E':'median_age'  # median age
    ,'B23006_023E':'total_bach_degree' # total Bach degree
    ,'B06009_003E':'total_high_school_graduate' # total high school graduate
    ,'B05009_001E':'total_under_18' # total voting age population (divide ed. att. by this)
    ,'B25077_001E':'median_home_value' # median home value 
    # ,'B25031_001E':'median_gross_rent' # median gross rent 
    ,'B02009_001E':'total_black_population' # black pop
    ,'B02001_002E':'total_white_population' # white
    ,'B03002_012E':'total_hispanic_population' # hispanic
    ,'B02011_001E':'total_asian_population' # asian
    # ,'B25010_001E':'avg_hh_size' # average household size
    ,'B25008_001E':'total_population_in_housing' # total population in occupied housing
    ,'B25001_001E':'total_housing_units'
    ,'B25106_002E':'total_owner_occupied_housing_units' # total owner occupied housing units
    ,'B25106_024E':'total_renter_occupied_housing_units' # total renter occupied housing units
    ,"B19083_001E":'income_gini' # "income_gini"
}


census_features_list = list(census_features.keys())

historic_census_features = {
     'B02001_001E':'total_population'  # population amnt
    # ,'B05009_001E':'total_under_18' # total voting age population (divide ed. att. by this)
    ,'B25077_001E':'median_home_value' # median home value 
    ,'B02009_001E':'total_black_population' # black pop
    ,'B02001_002E':'total_white_population' # white
    ,'B03002_012E':'total_hispanic_population' # hispanic
    ,'B02011_001E':'total_asian_population' # asian
    ,'B25008_001E':'total_population_in_housing' # total population in occupied housing
    ,'B25001_001E':'total_housing_units'
    ,'B25106_002E':'total_owner_occupied_housing_units' # total owner occupied housing units
    ,'B25106_024E':'total_renter_occupied_housing_units' # total renter occupied housing units
    ,"B19083_001E":'income_gini' # "income_gini"
}

census_features_list = list(census_features.keys())
historic_census_features_list = list(historic_census_features.keys())
num_sqft = 100000

# pull data
def pull_data(state,counties,year=2020):
    if type(counties)!= list:
        counties = [counties]
    if year !=2020:
        features = historic_census_features_list
    else:
        features = census_features_list
    for c in counties:
        d = censusdata.download('acs5', year,
               censusdata.censusgeo([('state', states.lookup(state).fips),
                                     ('county', c),
                                     ('tract', '*')]),
                                     features)
        
        if 'data' in locals():
            data = pd.concat([data,d])
        else:
            data = d
        
    # Clean some of the census data  
        # reindex
    data.index = data.index.astype(str).str.split(',').str[0] + ' ' + data.index.astype(str).str.split(',').str[3].str.split('>').str[1].str.split(':').str[1] 
        # rename columns
    data.rename(columns=census_features,inplace=True)
        
        # replace nonsensical/NA values
    for col in data.columns:
        data[col].fillna(data[col].astype(float).mean(),inplace=True)
        data[col].replace(-666666666,data[col].astype(float).mean(),inplace=True)
    
    data.drop_duplicates(inplace=True)
    
    # Pull Geo data
    file = pull_census_tract_geodata(state,year)
    file.index = file['NAMELSAD'] + ' ' + file['COUNTYFP']
    data = gpd.GeoDataFrame(data.merge(file,'left',right_on=file.index,left_on=data.index)).drop(columns=['TRACTCE','NAMELSAD'])
    
    # Final Cleaning
    data.rename(columns={'key_0':'tract'
                        ,'INTPTLAT': 'lat'
                        ,'INTPTLON':'lng'},inplace=True)
    data.index = data.tract
    data.drop(columns='tract',inplace=True)
    
    # Pull square area of tract & clean some geodata
    data.lat = data.lat.str.replace('+','')
    data.lng = data.lng.str.replace('+','')
    
    data[f'{num_sqft}_sqft'] = data.to_crs(epsg=5070).area / num_sqft # Get 1000 sq. footage

    return data
    
    
def std_census_data(census_data,year=2020):
    census_data = copy.deepcopy(census_data)
    # remove data rows with 0 population or 0 housing units (nonuccupancy areas)
    census_data = census_data[census_data['total_population']>0]
    census_data = census_data[census_data['total_housing_units']>0]
    if 'median_hh_income' in census_data.columns: 
        census_data['total_18_+'] = census_data['total_population'] - census_data['total_under_18'] #final total population over 18
        census_data['percent_bachelor_degree'] = census_data['total_bach_degree']/census_data['total_18_+']  # % of voting age population
        census_data['percent_high_school_graduate'] =census_data['total_high_school_graduate']/census_data['total_18_+']   # % of voting age population
        census_data['percent_over_18'] =  census_data['total_18_+']/census_data['total_population'] # % population over 18
    
    census_data['population_density'] = census_data['total_population'] / census_data[f'{num_sqft}_sqft']  # people per area. 
    census_data['percent_bl'] = census_data['total_black_population']/census_data['total_population'] # % population black
    census_data['percent_wh'] = census_data['total_white_population']/census_data['total_population'] # % population white
    census_data['percent_his'] = census_data['total_hispanic_population']/census_data['total_population']# % population hispanic
    census_data['percent_as'] = census_data['total_asian_population']/census_data['total_population']# % population asian
    # census_data['percent_population_housed'] = census_data['total_population_in_housing']/census_data['total_population'] # %population housed
    census_data['percent_homes_occupied_by_owner'] = census_data['total_owner_occupied_housing_units']/census_data['total_housing_units'] # %  homes occupied by owner
    census_data['percent_homes_occupied_by_renter'] = census_data['total_renter_occupied_housing_units']/census_data['total_housing_units']# %  homes occupied by renter
    census_data['diversity_index'] = census_data.apply(lambda row: 
                                                       distribution_index([row['percent_bl'],row['percent_his'],row['percent_as'],row['percent_wh']])
                                                       ,axis=1) #diversity index with KL divergence
    
    cols_2020 = ['total_population','population_density', 'median_age',
                'median_hh_income', 'median_home_value',
                'income_gini', 'diversity_index', 
                'percent_bachelor_degree', 'percent_high_school_graduate','percent_over_18',
                'percent_homes_occupied_by_owner', 'percent_homes_occupied_by_renter',
                'STATEFP','COUNTYFP', 'GEOID', 'NAME', 'MTFCC', 'FUNCSTAT', 'ALAND', 'AWATER','lat', 'lng', 'geometry', f'{num_sqft}_sqft' ]
    
    cols_other = ['total_population', 
                'median_home_value',
                'income_gini', 'diversity_index',
                'percent_homes_occupied_by_owner', 'percent_homes_occupied_by_renter',
                'GEOID']
    census_data = pd.DataFrame(census_data)
    if year == 2020:
        census_data = census_data[census_data.columns.intersection(cols_2020)]
    else:
        census_data = census_data[census_data.columns.intersection(cols_other)]
        census_data.columns = f'_{year}_' + census_data.columns 
        census_data.rename(columns={f'_{year}_GEOID':'GEOID'},inplace=True)
        
    return census_data

def distribution_index(compared_dist, base_dist='uniform'): # calculates relative entropy given a number of columns with %
    dist_mean = np.array(compared_dist).mean()
    
    if base_dist == 'uniform':
        base_dist = [dist_mean]
        for i in range(len(compared_dist)-1):
            base_dist.append(dist_mean)
    else:
        print('Not an acceptable distribution')
    return -rel_entr(compared_dist,base_dist).sum()


def pull_historic_census_data(census_data): # pulls in all historic data. Takes raw or cleaned input dataframe (will clean if not already)
    census_data = copy.deepcopy(census_data)
    if 'percent_wh' in census_data.columns: #this is uncleaned data
        census_data = std_census_data(census_data)# clean data if not already cleaned
    counties = list(census_data.COUNTYFP.dropna().astype(str).unique())
    state = str(census_data.STATEFP.iloc[0])
    # 5 YEARS BACK
    _2015 = std_census_data(pull_data(state,counties,year=2015),2015)
    census_data['tract'] = census_data.index # to keep our tract name
    census_data = pd.merge(census_data,_2015, how='left',left_on='GEOID',right_on='GEOID')
    
    # 10 YEARS BACK 
    _2010 = std_census_data(pull_data(state,counties,year=2010),2010)
    census_data = pd.merge(census_data,_2010, how='left',left_on='GEOID',right_on='GEOID')
    
    census_data['10_y_population_%_change'] = census_data.apply(lambda row:percent_change(row['total_population'],row['_2010_total_population'])
                                                      , axis=1)
    
    census_data['10_y_median_home_value_%_change'] = census_data.apply(lambda row: percent_change(row['median_home_value'],row['_2010_median_home_value']),axis=1)
    census_data['10_y_income_gini_%_change'] = census_data.apply(lambda row: percent_change(row['income_gini'],row['_2010_income_gini']),axis=1)
    census_data['10_y_diversity_index_%_change'] = census_data.apply(lambda row: percent_change(row['diversity_index'],row['_2010_diversity_index']),axis=1)
    census_data['10_y_percent_homes_occupied_by_owner_%_change'] = census_data.apply(lambda row: row['percent_homes_occupied_by_owner'] - row['_2010_percent_homes_occupied_by_owner'] ,axis=1)
    census_data['10_y_percent_homes_occupied_by_renter_%_change'] = census_data.apply(lambda row: row['percent_homes_occupied_by_renter'] - row['_2010_percent_homes_occupied_by_renter'],axis=1)

    census_data['5_y_population_%_change'] = census_data.apply(lambda row: percent_change(row['total_population'],row['_2015_total_population']),axis=1)
    census_data['5_y_median_home_value_%_change'] = census_data.apply(lambda row: percent_change(row['median_home_value'],row['_2015_median_home_value']),axis=1)
    census_data['5_y_income_gini_%_change'] = census_data.apply(lambda row: percent_change(row['income_gini'],row['_2015_income_gini']),axis=1)
    census_data['5_y_diversity_index_%_change'] = census_data.apply(lambda row: percent_change(row['diversity_index'],row['_2015_diversity_index']),axis=1)
    census_data['5_y_percent_homes_occupied_by_owner_%_change'] = census_data.apply(lambda row: row['percent_homes_occupied_by_owner'] - row['_2015_percent_homes_occupied_by_owner'],axis=1)
    census_data['5_y_percent_homes_occupied_by_renter_%_change'] = census_data.apply(lambda row: row['percent_homes_occupied_by_renter'] - row['_2015_percent_homes_occupied_by_renter'],axis=1)
    
    census_data.index = census_data['tract']
    #clean data: 
        # only return needed columns
    final_cols = ['population_density',
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
 
        'STATEFP', 'COUNTYFP', 'GEOID', 'NAME', 'MTFCC','FUNCSTAT', 'ALAND', 'AWATER', 'lat', 'lng', 'geometry', f'{num_sqft}_sqft',
      ]
    
    census_data = census_data[final_cols]
    
    return census_data
    
def percent_change(x2,x1):
    if x1 !=0:
        return (x2-x1)/x1
    else: 
        return 'error here!'

# Pulling functions
def pull_school_data(state,counties):
    
    if type(counties)!=list:
        counties = [counties]
        
    # data
    for c in counties:
        q = f"""SELECT name,ratingScale,parentRating,lat,lon as lng
        FROM `homevest-data.nbhd_similarity.greatschools_{state_fips(state)}{c}`"""
        if 'df' in locals():
            df = pd.concat([df,bq_to_df(q)])
        else:
            df = bq_to_df(q)
    
    df = df[df['ratingScale'] != 'None']
    
    #clean
    df['school_rating'] = df['ratingScale'].apply(lambda x: 1 if x =='Below average' else (3 if x =='Above average' else 2))
    df.drop(columns=['ratingScale','parentRating'],inplace=True)
    
    #Geospatial Conversions
 
    geometry = [Point(xy) for xy in zip(df.lng, df.lat)]
    df = df.drop(columns = ['lng', 'lat'])
    
    gdf = gpd.GeoDataFrame(df, crs="EPSG:4326", geometry=geometry).to_crs(epsg=3763)
    buffer_length_in_meters = 5 * 1609.344 # 5 mile buffer
    gdf['geometry'] = gdf.geometry.buffer(buffer_length_in_meters)
    gdf = gdf.to_crs(epsg=4269)
    
    # Pull in census tract
    file = pull_census_tract_geodata(state)
    file.index = file['NAMELSAD'] + ' ' + file['COUNTYFP']
    file.drop(columns=['STATEFP',
                       # 'COUNTYFP',
                       'TRACTCE','GEOID','NAME','NAMELSAD','MTFCC','FUNCSTAT','ALAND','AWATER','INTPTLAT','INTPTLON'],inplace=True)
    
    # Assign school to census tract
    gdf = gpd.sjoin(gdf, file, how='left').rename(columns={'index_right':'tract'})
    
    #get tract average school rating
    gdf = pd.DataFrame(gdf.groupby('tract').mean())
    
    return gdf

def amenity_categories(amenity_group):
    ag = {'city_life':['arcade','parking'],
          'cultural':['art_gallery','library'],
          'greenery':['lake','park'],
          'retail':['mall','retail_store'],
          'negative':['police_station','bail_bonds'],
    }
       
    return ag[amenity_group][0],ag[amenity_group][1]
    
def pull_gmaps_amenities(state, counties, amenity_group='city_life', query=False): # [CAN ADD FUNCTIONALITY TO TAKE DIFFERENT QUERY IF NAMING/STORING CONVENTION IS DIFFERENT FOR AREA]
        
    if type(counties)!=list: 
        counties = [counties]
        
    amenity_1,amenity_2 = amenity_categories(amenity_group)

    for c in counties:
        q = f""" SELECT name,rating,lat,lng FROM `homevest-data.nbhd_similarity.gmaps_{amenity_1}_{state_fips(state)}{c}`
        UNION DISTINCT 
        SELECT name,rating,lat,lng FROM `homevest-data.nbhd_similarity.gmaps_{amenity_2}_{state_fips(state)}{c}`"""
        if 'df' in locals():
            df = pd.concat([df,bq_to_df(q)])
        else:
            df = bq_to_df(q)
        
    #Geospatial Conversions
 
    geometry = [Point(xy) for xy in zip(df.lng, df.lat)]
    df = df.drop(columns = ['lng', 'lat'])
    
    gdf = gpd.GeoDataFrame(df, crs="EPSG:4326", geometry=geometry).to_crs(epsg=3763)
    buffer_length_in_meters = 1 * 1609.344 # 5 mile buffer
    gdf['geometry'] = gdf.geometry.buffer(buffer_length_in_meters)
    gdf = gdf.to_crs(epsg=4269)
    
    
    
    # Pull in census tract
    file = pull_census_tract_geodata(state)
    file.index = file['NAMELSAD'] + ' ' + file['COUNTYFP']
    file.drop(columns=['STATEFP',
                       'COUNTYFP',
                       'TRACTCE','GEOID','NAME','NAMELSAD','MTFCC','FUNCSTAT','ALAND','AWATER','INTPTLAT','INTPTLON'],inplace=True)
    
    # Assign to census tract
    gdf = gpd.sjoin(gdf, file, how='left').rename(columns={'index_right':'tract'})

    gdf[f'{num_sqft}_sqft'] = gdf.to_crs(epsg=5070).area / num_sqft # Get sq. footage
    gdf = pd.DataFrame(gdf)
    gdf = gdf.groupby('tract').agg({"rating": "mean",
                                 "name" :"count",
                                  f'{num_sqft}_sqft':"mean"
                                 })
    
    gdf[f'{amenity_group}_density'] = gdf['name']/gdf[f'{num_sqft}_sqft']
    gdf = gdf.drop(columns=[f'{num_sqft}_sqft','name']).rename(columns = {'rating':f'{amenity_group}_rating'})
    gdf.fillna(0,inplace=True)
    
    if amenity_group == 'negative':
        gdf.drop(columns='negative_rating',inplace=True)
        
    return gdf

def pull_yelp_amenity(state, counties, amenity,query=False): # [CAN ADD FUNCTIONALITY TO TAKE DIFFERENT QUERY IF NAMING/STORING CONVENTION IS DIFFERENT FOR AREA]
        
    if type(counties)!=list: 
        counties = [counties]
    
    #get list of cbsas for thing
    cbsas = []
    for c in counties:
        cbsas.append(cbsa_fips_code(state,c))
    
    for cbsa in set(cbsas):
        q = f""" 
        SELECT name, rating ,latitude as lat, longitude as lng FROM `homevest-data.nbhd_similarity.yelp_{amenity}_{cbsa}`
            """
        if 'df' in locals():
            df = pd.concat([df,bq_to_df(q)])
        else:
            df = bq_to_df(q)
        
    #Geospatial Conversions
    geometry = [Point(xy) for xy in zip(df.lng, df.lat)]
    df = df.drop(columns = ['lng', 'lat'])
    
    gdf = gpd.GeoDataFrame(df, crs="EPSG:4326", geometry=geometry).to_crs(epsg=3763)
    buffer_length_in_meters = 1 * 1609.344 # 5 mile buffer
    gdf['geometry'] = gdf.geometry.buffer(buffer_length_in_meters)
    gdf = gdf.to_crs(epsg=4269)
    
    
    # Pull in census tract
    file = pull_census_tract_geodata(state)
    file.index = file['NAMELSAD'] + ' ' + file['COUNTYFP']
    file.drop(columns=['STATEFP',
                       'COUNTYFP',
                       'TRACTCE','GEOID','NAME','NAMELSAD','MTFCC','FUNCSTAT','ALAND','AWATER','INTPTLAT','INTPTLON'],inplace=True)
    
    # Assign to census tract
    gdf = gpd.sjoin(gdf, file, how='left').rename(columns={'index_right':'tract'})

    gdf[f'{num_sqft}_sqft'] = gdf.to_crs(epsg=5070).area / num_sqft # Get sq. footage
    gdf = pd.DataFrame(gdf)
    gdf = gdf.groupby('tract').agg({"rating": "mean",
                                 "name" :"count",
                                  f'{num_sqft}_sqft':"mean"
                                 })
    
    gdf[f'{amenity}_density'] = gdf['name']/gdf[f'{num_sqft}_sqft']
    gdf = gdf.drop(columns=[f'{num_sqft}_sqft','name']).rename(columns = {'rating':f'{amenity}_rating'})
    gdf.fillna(0,inplace=True)
    return gdf

def csv_to_geodataframe(path=''): #for stored data
    gdf = pd.read_csv(path,index_col='tract')
    
    gdf['geometry'] = gpd.GeoSeries.from_wkt(gdf['geometry'])

    gdf = gpd.GeoDataFrame(gdf, geometry='geometry')
    gdf.crs = 'EPSG:4269'
    return gdf

def csv_to_geodataframe(path=''): #for stored data
    gdf = pd.read_csv(path,index_col='tract')
    
    gdf['geometry'] = gpd.GeoSeries.from_wkt(gdf['geometry'])

    gdf = gpd.GeoDataFrame(gdf, geometry='geometry')
    gdf.crs = 'EPSG:4269'
    return gdf

def pull_all_data(state,county):
    data = pull_data(state,county)
    cleaned_data = std_census_data(data)
    print(f'pulling historic data for {state}..')
    all_data = pull_historic_census_data(cleaned_data)
    print('3/11')
    schools_data = pull_school_data(state,county)
    # gmaps_data_city_life = pull_gmaps_amenities(state,county, amenity_group='city_life')
    gmaps_data_cultural = pull_gmaps_amenities(state,county, amenity_group='cultural')
    gmaps_data_greenery = pull_gmaps_amenities(state,county, amenity_group='greenery')
    print('5/11...')
    gmaps_data_retail = pull_gmaps_amenities(state,county, amenity_group='retail')
    gmaps_data_negative = pull_gmaps_amenities(state,county, amenity_group='negative')
    print('7/11')
    yelp_restaurants = pull_yelp_amenity(state, county, amenity='restaurants')
    yelp_nightlife = pull_yelp_amenity(state, county, amenity='nightlife')
    yelp_fitness = pull_yelp_amenity(state, county, amenity='fitness')
    print('pulled all data!')

    # merge all data
    #     school data
    df = pd.merge(all_data,schools_data,how='left',left_index=True,right_index=True)
    
    # amenities data merges
        #cultural
    df = pd.merge(df,gmaps_data_cultural,how='left',left_index=True,right_index=True)
    print('merging..')
        # greenery
    df = pd.merge(df,gmaps_data_greenery,how='left',left_index=True,right_index=True)
        # retail
    df = pd.merge(df,gmaps_data_retail,how='left',left_index=True,right_index=True)
        #negative
    df = pd.merge(df,gmaps_data_negative,how='left',left_index=True,right_index=True)
    print('almost done...')

        #restaurants
    df = pd.merge(df,yelp_restaurants,how='left',left_index=True,right_index=True)
        #fitness
    df = pd.merge(df,yelp_nightlife,how='left',left_index=True,right_index=True)
        #nightlife
    df = pd.merge(df,yelp_fitness,how='left',left_index=True,right_index=True)
    print('done!!!')

    df['geometry'] = df.geometry.astype(str)
    df.fillna(0,inplace=True)
    return df



