import json
from botocore.vendored import requests
import sys, os
import urllib
import time, datetime

# This client code can run on Python 2.x or 3.x.  Your imports can be
# simpler if you only need one of those.
try:
    # For Python 3.0 and later
    from urllib.error import HTTPError
    from urllib.parse import quote
    from urllib.parse import urlencode
except ImportError:
    # Fall back to Python 2's urllib2 and urllib
    from urllib2 import HTTPError
    from urllib import quote
    from urllib import urlencode

# API constants, you shouldn't have to change these.
API_HOST = 'https://api.yelp.com'
SEARCH_PATH = '/v3/businesses/search'
BUSINESS_PATH = '/v3/businesses/'  # Business ID will come after slash.
SEARCH_LIMIT = 3

DEFAULT_TERM = 'dinner'
DEFAULT_LOCATION = 'New York'
DEFAULT_TIME = '2018-04-06'


def request(host, path, api_key, url_params=None):
    """Given your API_KEY, send a GET request to the API.
    Returns:
        dict: The JSON response from the request.
    Raises:
        HTTPError: An error occurs from the HTTP request.
    """
    url_params = url_params or {}
    url = '{0}{1}'.format(host, quote(path.encode('utf8')))
    headers = {
        'Authorization': 'Bearer %s' % api_key,
    }
    #print(u'Querying {0} ...'.format(url))
    response = requests.request('GET', url, headers=headers, params=url_params)
    return response.json()

def search(api_key, term, location, open_time):
    #open-time = "2018-03-22-21-00"
    #UTC_OFFSET_TIMEDELTA = datetime.datetime.utcnow() - datetime.datetime.now()
    #utc_datetime = local_datetime + UTC_OFFSET_TIMEDELTA
    local_datetime = datetime.datetime.strptime(open_time, "%Y-%m-%d-%H-%M")
    timestamp = local_datetime.timestamp()
    url_params = {
        'term': term.replace(' ', '+'),
        'location': location.replace(' ', '+'),
        #An integer represending the Unix time in the same timezone of the search location. 
        #If specified, it will return business open at the given time.
        'open_at': str(int(timestamp)).replace(' ', '+'),
        'limit': SEARCH_LIMIT
    }
    return request(API_HOST, SEARCH_PATH, api_key, url_params=url_params)

def get_business(api_key, business_id):
    business_path = BUSINESS_PATH + business_id
    return request(API_HOST, business_path, api_key)

#open-time = "2018-03-22-21-00" (YYYY-MM-DD-hh-mm)
def query_api(term, location, o_date, o_time):
    """Queries the API by the input values from the user.
    Args:
        term (str): The search term to query.
        location (str): The location of the business to query.
    """
    res = []
    open_time = o_date + '-' + o_time
    response = search(API_KEY, term, location, open_time)
    businesses = response.get('businesses')
    if not businesses:
        print(u'No businesses for {0} in {1} found.'.format(term, location))
        return res

    for business in businesses:
        name = business['name']
        category = ""
        if len(business['categories']) > 0:
            category = business['categories'][0]['title']
        location = ','.join(business['location']['display_address'])
        res.append((category, name, location, business['price']))
    return res

def main():
    os.environ['TZ'] = 'America/New_York'
    time.tzset()

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-q', '--term', dest='term', default=DEFAULT_TERM,
                        type=str, help='Search term (default: %(default)s)')
    parser.add_argument('-l', '--location', dest='location',
                        default=DEFAULT_LOCATION, type=str,
                        help='Search location (default: %(default)s)')
    parser.add_argument('-t', '--time', dest='time',
                        default=DEFAULT_TIME, type=str,
                        help='Search location (default: %(default)s)')
 
    input_values = parser.parse_args()
    try:
        res = query_api(input_values.term, input_values.location, input_values.time, "18-30")
        print(res)
    except HTTPError as error:
        sys.exit(
            'Encountered HTTP error {0} on {1}:\n {2}\nAbort program.'.format(
                error.code,
                error.url,
                error.read(),
            )
        )

if __name__ == '__main__':
    main()



