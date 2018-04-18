import json
import dateutil.parser
import datetime
import time
import os
import math
import random
import logging
import session

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

DINING_SUGGESTION_INTENT_NAME = 'DiningSuggestionsIntent'


def dining(intent):
    location = intent["currentIntent"]["slots"]["Location"]
    cuisine = intent["currentIntent"]["slots"]["Cuisine"]
    dining_date = intent["currentIntent"]["slots"]["Date"]
    dining_time = intent["currentIntent"]["slots"]["Time"]
    people = intent["currentIntent"]["slots"]["PeopleNum"]
    phone = intent["currentIntent"]["slots"]["Phone"]
    logger.debug(intent["currentIntent"]["slots"])
    
    #send message to sqs
    import sqs
    msg_attrs = {}
    msg_attrs['Location'] = location
    msg_attrs['Cuisine'] = cuisine
    msg_attrs['Date'] = dining_date
    msg_attrs['Time'] = dining_time
    msg_attrs['PeopleNum'] = people
    msg_attrs['Phone'] = phone
    msg_body = "test"
    sqs.send_message(msg_attrs, msg_body)
    output_session_attributes = intent['sessionAttributes'] if intent['sessionAttributes'] is not None else {}
    return session.close(output_session_attributes,
                            'Fulfilled',
                            {
                                'contentType': 'PlainText',
                                'content': 'You’re all set. Expect my recommendations shortly! Have a good day.'
                            }
                        )

def dispatch(intent_request):
    #logger.debug('dispatch userId={}, intentName={}'.format(intent_request['userId'], intent_request['currentIntent']['name']))
    intent_name = intent_request['currentIntent']['name']
    # Dispatch to your bot's intent handlers
    if intent_name == DINING_SUGGESTION_INTENT_NAME:
        return dining(intent_request)
    raise Exception('Intent with name ' + intent_name + ' not supported')

def handler(event, context):
    # By default, treat the user request as coming from the America/New_York time zone.
    os.environ['TZ'] = 'America/New_York'
    time.tzset()
    logger.debug('event.bot.name={}'.format(event['bot']['name']))
    return dispatch(event)

def main():
    context = None
    event = {}
    event["bot"] = {}
    event["bot"]["alias"] = "$LATEST"
    event["bot"]["version"] = "$LATEST"
    event["bot"]["name"] = "DINING"
    event["currentIntent"] = {}
    event["currentIntent"]["name"] = DINING_SUGGESTION_INTENT_NAME
    event["currentIntent"]["slots"] = {}
    event["currentIntent"]["slots"]["Location"] = "New York"
    event["currentIntent"]["slots"]["Cuisine"] = "Chinese"
    event["currentIntent"]["slots"]["Date"] = "2018-03-24"
    event["currentIntent"]["slots"]["Time"] = "21-00"
    event["currentIntent"]["slots"]["PeopleNum"] = "2"
    event["currentIntent"]["slots"]["Phone"] = "1234567890"
    event["sessionAttributes"] = {}
    lambda_handler(event, context)

if __name__ == "__main__":
    main()



