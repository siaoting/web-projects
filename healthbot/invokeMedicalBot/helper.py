import json
from urllib2 import urlopen


def get_location():
	#url = 'http://ipinfo.io/json'
	#response = urlopen(url)
	#data = json.load(response)
	#ip = data['ip']
	#loc = data['loc'].split(',')
	loc = ['40.7280', "-73.9453"]
	#print 'Location : {} {}'.format(loc[0], loc[1])
	return (loc[0], loc[1])
	
def main():
	get_location()

if __name__ == '__main__':
    main()
