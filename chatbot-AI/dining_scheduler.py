import time, datetime
import os
import logging
import yelp
import sns

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
    
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

def build_suggestion(dining_setting, restaurants):
    cuisine = dining_setting['Cuisine']
    location = dining_setting['Location']
    dining_date = dining_setting['Date']
    dining_time = dining_setting['Time']
    people_num = dining_setting['PeopleNum']
    people = "person" if (int(people_num)) == 1 else "people"
    display_dining_date = "today" if dining_date == time.strftime("%Y-%m-%d") else dining_date
    display_dining_time = datetime.datetime.strptime(dining_time, '%H-%M').strftime('%I:%M %p')

    if not restaurants:
        suggestions = "Hello! There are no suggestions for %s restaurant for %s %s for %s at %s." % \
                (cuisine, people_num, people, display_dining_date, display_dining_time)
        return suggestions

    suggestions = "Hello! Here are my suggestions for %s restaurant for %s %s, " % \
                  (cuisine, people_num, people)
    suggestions += "for %s at %s: " % (display_dining_date, display_dining_time)
    for i in range(len(restaurants)):
        if restaurants[i][0]:
            suggestions += "({} Restaurant {}):".format(restaurants[i][0], i + 1)
        else:
            suggestions += "(Restaurant {}):".format(i + 1)
        suggestions += " %s, located at %s, price as %s. " % (restaurants[i][1], restaurants[i][2], restaurants[i][3])
    suggestions += "Enjoy your meal!"
    logger.debug(suggestions)
    return suggestions

def handler(event, context):
    os.environ['TZ'] = 'America/New_York'
    time.tzset()
    cur_time = datetime.datetime.fromtimestamp(int(time.time())).strftime('%Y-%m-%d-%H:%M')
    logger.debug("invokeChatBotScheduler %s" % (cur_time))
    
    #receive and delete messages
    import sqs
    dining_setting = sqs.receive_message()
    logger.debug("dining_setting: {}".format(dining_setting))
    if not dining_setting:
        return None
    dining_setting['Time'] = dining_setting['Time'].replace(":", '-')
    cuisine = dining_setting['Cuisine']
    location = dining_setting['Location']
    dining_date = dining_setting['Date']
    dining_hour = dining_setting['Time']
    phone = dining_setting['Phone']
    
    #yelp
    try:
        restaurants = yelp.query_api(cuisine, location, dining_date, dining_hour)
        logger.debug(restaurants)
        suggestions = build_suggestion(dining_setting, restaurants)
        #print("sending message to {}".format(phone))
        sns.send_message('1'+ phone, suggestions)
        
    except HTTPError as error:
        logger.debug('Encountered HTTP error {0} on {1}:\n {2}\nAbort program.'.format(
                error.code,
                error.url,
                error.read()))
    
    return None

def main():
    event, context = None, None
    handler(event, context)

if __name__ == "__main__":
    main()



