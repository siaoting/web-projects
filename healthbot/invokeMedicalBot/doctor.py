import json
import helper
from urllib2 import urlopen

API_KEY=''

def get_doctor(field, lat, lon):
    distance = 1500
    url = 'https://api.betterdoctor.com/2016-03-01/doctors?'
    url += 'query={}&'.format(field)
    url += 'location={}%2C{}%2C{}&user_location={}%2C{}'.format(lat, lon, distance, lat, lon)
    url += '&skip=0&limit=3&user_key={}'.format(API_KEY)
    response = urlopen(url)
    data = json.load(response)
    data = data['data']
    if not data or 'practices' not in data[0]:
        return (None, None, None)
    res = []
    for i in range(len(data)): 
        cur_data = data[i]['practices']
        hospital = cur_data[0]['name']
        if 'phones' not in cur_data[0] or not cur_data[0]['phones']:
            return (None, None, None)
        phone = cur_data[0]['phones'][0]['number']
        addr_obj = cur_data[0]['visit_address']
        addr = "{}, {} City, {}".format(addr_obj['street'], addr_obj['city'], addr_obj['state_long'])
        res.append((hospital, phone, addr))
    return res

def main():
    get_doctor('Toothache')

if __name__ == '__main__':
    main()
