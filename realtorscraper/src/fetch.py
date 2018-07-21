'''
functions that will
    - retrieve realtor listings from within geographic boundaries, 
    - minimally process records, 
    - store the retrieved records as a csv file in ../data

    * since the api can't return more than 200 records at a time, the record fetch function recursively calls itself on two halves of the geogrphical rectangle it originally wanted to fetch, until each call returns less than 200 records
    !Therefore, this 'binary search' algo will fail if, roughly speaking, more than 200 units are for sale in a conf.EPSILON wide rectangle! This should not be an issue if the original rectangle provided has reasonable (say, on the scale of a city) height.
'''

from ..etc import conf

import pandas as pd
import re
import datetime
import os.path
import requests

def get_request_params(location):
    '''
    given valid
        location
    returns
        original request parameters
    '''
        # setting parameters for 
    params = {
        'MaxRecords':'200', #crap
        'RecordsPerPage':'200', #crap
        'CultureId':'1', #?
        'ApplicationId':'1', #?
        #'MaximumResults':'100000', #don't want this
        #'StoreyRange':'0-0',
        #'BedRange':'0-0',
        #'BathRange':'0-0',
        'PropertySearchTypeId':'1',
        'TransactionTypeId':'2',
            # rectangular geographic boundaries
        'LongitudeMin':conf.LOCATIONS[location]['LONGITUDE_MIN'],
        'LongitudeMax':conf.LOCATIONS[location]['LONGITUDE_MAX'],
        'LatitudeMin':conf.LOCATIONS[location]['LATITUDE_MIN'],
        'LatitudeMax':conf.LOCATIONS[location]['LATITUDE_MAX'],
        'SortOrder':'A',
        'SortBy':'1',
        #'viewState':'l',
        #'ZoomLevel':'10',
        #'PropertyTypeGroupID':'1',
        #'NumberofDays':'13',
        #'PriceMax':'150000',
        #'CurrentPage':'3', #loop using this did not work
    }
    return params

def get_response(params):
    '''
    given proper request 
        params, 
    returns 
        (n records, json response)
    '''
    response = requests.get(conf.API_URL, params=params)
    
    print 'code:'+ str(response.status_code)
    if response.status_code == 200:
        #print '******************'
        #print 'headers:'+ str(response.headers)
        print '******************'
        js = response.json()
        print 'paging:'+ str(js['Paging'])
    
        total_records = js['Paging']['TotalRecords']
    
        return total_records, response
    else:
        print 'request failed with params ', params


def dataframe_from_json(js):
    '''
    given   
        response data from json 
    returns 
        data as pandas dataframe
    '''
    df = pd.DataFrame(js['Results'])
    print 'records: ', len(df)

    df['latitude'] = df['Property'].apply(lambda x: float(x['Address']['Latitude']))
    df['longitude'] = df['Property'].apply(lambda x: float(x['Address']['Longitude']))
    df['address'] = df['Property'].apply(lambda x: x['Address']['AddressText'])
    df['price'] = df['Property'].apply(lambda x: float(re.sub( r'[^\d]', '', x['Price'])) )
             
    df['type'] = df['Building'].apply(lambda x:x['Type'] if 'Type' in x.keys() else None)
    
    print 'records final: ', len(df)        
    return df

def append_records(params, dfs):
    '''
    given 
        (request params, records already fethed)
    returns
        (concatenated old+new records)
    since the api can't return more than 200 records at a time, recursively calls itself on two halves of the rectangle it originally wanted to fetch, until each call returns less than 200 records
    '''
    print 'n records fetched to date ', len(dfs)
    
    total_records, response = get_response(params)
    print 'new records fetched : ', total_records

    if total_records <= 200:
            # appending records from current rectangle
        js = response.json()
        df = dataframe_from_json(js)
        dfs.append( df )
        return dfs
    else:
            # fetching records on the two halves of the previous rectangle
        longitude_midpoint_plus = str((float(params['LongitudeMin']) + float(params['LongitudeMax']))/2. + conf.EPSILON)
        longitude_midpoint_minus = str((float(params['LongitudeMin']) + float(params['LongitudeMax']))/2. - conf.EPSILON)
            
        params_1 = params.copy()
        params_1['LongitudeMax'] = longitude_midpoint_plus
        dfs = append_records(params_1, dfs)
        
        params_2 = params.copy()
        params_2['LongitudeMin'] = longitude_midpoint_minus
        dfs = append_records(params_2, dfs)
        
        return dfs

def get_records(params):
    '''
    '''
    dfs = []
    dfs = append_records(params, dfs)
    df = pd.concat(dfs, axis=0)
    df = df.drop_duplicates(subset=['Id']) # !tolerance conf.EPSILON will create duplicate records
    print 'retrieved ', len(df), ' records '
    return df

def save(df):
    '''
    writing dataframe to csv
    '''
    date = str(datetime.datetime.now().date())
    save_path = os.path.join(conf.DATA_PATH, 'listings_%s.csv'%date)
    print 'saving to ', save_path
    df.to_csv(save_path, encoding='utf-8')

