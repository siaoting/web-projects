import logging
import os, time
import json
import boto3, dynamo
from nutrition import Nutrition


logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

FOOD_INTENT_NAME='FoodIntent'
username = None

def fulfill(content):
    return {
        'sessionAttributes': {},
        "dialogAction": {
            "type": "Close",
            "fulfillmentState": "Fulfilled",
            "message": {
                "contentType": "PlainText",
                "content": content
                }
            }
    }

def delegate(session_attributes, slots):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Delegate',
            'slots': slots
        }
    }

def process_food(slots, food):
    nutrition_obj = Nutrition()
    cals = nutrition_obj.getCals(food)
    if cals > 0:
        content = 'You just ate {}, which on an average has {} Calories. And your food is set!'.format(food, cals)
        dynamo.put_item_food(username, food, cals)
    else:
        content = 'We are unable to find the calories for {}'.format(food)
    return fulfill(content) 

def food(intent):
    session_attributes = intent['sessionAttributes'] if intent['sessionAttributes'] is not None else {}
    slots = intent["currentIntent"]["slots"]
    food_slot = slots["food"]
    if not food_slot:
        return delegate(session_attributes, slots)
    return process_food(slots, food_slot)
    
def dispatch(intent_request):
    intent_name = intent_request['currentIntent']['name']
    # Dispatch to your bot's intent handlers
    if intent_name == FOOD_INTENT_NAME:
        return food(intent_request)

    raise Exception('Intent with name ' + intent_name + ' not supported')

def handler(event, context):
    os.environ['TZ'] = 'America/New_York'
    time.tzset()
    global username
    username = event['userId']
    logger.debug('event.bot.name={}'.format(event['bot']['name']))
    return dispatch(event)
