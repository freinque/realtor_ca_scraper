
# realtor.ca scraper
*What: scrape realtor.ca data using their api*

Why: I was not able to find a decent automated way of collecting realtor postings, so made this quick attempt. Successful at pulling a bunch of records daily since.

How: example usage
'''
python scrape.py --location=montreal
'''
this calls functions that will
    - retrieve (all, by default) realtor listings from within rectangular geographic boundaries ('montreal' location defined in realtorscraper/etc/conf.py in terms of max/min latitude/longitude), 
    - minimally process records, 
    - store the retrieved records as a csv file in ./data

NOTES
    * since the api can't return more than 200 records at a time, the record fetch function recursively calls itself on two halves of the geogrphical rectangle it originally wanted to fetch, until each call returns less than 200 records
    !Therefore, this 'binary search' algo will fail if, roughly speaking, more than 200 units are for sale in a conf.EPSILON wide rectangle! This should not be an issue if the original rectangle provided has reasonable (say, on the scale of a city) height.

