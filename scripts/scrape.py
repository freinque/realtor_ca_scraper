#!/usr/bin/env python
'''
script  that retrieves arguments (e.g. location) api request parameters, gets dataframe and saves data

'''
import os.path
import argparse

# TEMP, add package to your path outside of here
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

import realtorscraper.src.fetch

def main():
    parser = argparse.ArgumentParser(description='Retrieves listings from realtor.ca')
    parser.add_argument('--location', type=str, default='montreal',
                            help='key fron LOCATIONS in etc/conf.py')
    args = parser.parse_args()
    print 'fetching listings for location : ', args.location
        #retrieving params for request
    params = realtorscraper.src.fetch.get_request_params(args.location)
    
    df = realtorscraper.src.fetch.get_records(params)
    
    realtorscraper.src.fetch.save(df)

if __name__=='__main__':
    main()

