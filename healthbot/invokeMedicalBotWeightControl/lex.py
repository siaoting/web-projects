import logging
import os, time
import json
import boto3, dynamo
from nutrition import Nutrition


logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

WEIGHT_INTENT_NAME='WeightControlIntent'
username = None

def fulfill(session_attributes, content):
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

def get_weight(slots):
    weight = dynamo.query_weight(username)
    if weight:
        slots["weight"] = weight
    return weight

def add_weight(new_weight):
    weight = dynamo.query_weight(username)
    if not weight:
        dynamo.put_item_weight(username, new_weight)
    
def process_food(slots, weight):
    food, cals = dynamo.query_food(username)
    total = weight * 30
    cals = sum(cals)
    if not food:
        content = "Today, you did not eat anything yet. You can consume: {} calories. ".format(total)
    else:
        content = "Today, you ate: {}.".format(', '.join(food))
        content += ' It has a total of {} calories.'.format(cals)
    left = total-cals
    if left >= 0: 
        content += foodSuggest(left)
        content += ' Based on your weight, you can still consume {} calories for today. \n\n'.format(left)

    else:
        content += ' Based on your weight, you already exceeded your daily quote of {} calories.'.format(total)
    return fulfill({}, content)     
    
def foodSuggest(calories):
    calories_slot = str(calories)
    logger.debug("useid: {}, calories: {}".format(username, calories_slot))
    
    client = boto3.client('machinelearning')

    response = client.predict(
    MLModelId='ml-Te4fQ7Q9Iup',
    Record={
        'id': username,
        'calories' : calories_slot
    },
    PredictEndpoint='https://realtime.machinelearning.us-east-1.amazonaws.com'
    )
    
    foodItem = response['Prediction']['predictedLabel']
    content = "Also, For {} calories, you can try {}. ".format(calories_slot, foodItem)
    return content
    
def weight_control(intent):
    logger.debug(intent)
    session_attributes = intent['sessionAttributes'] if intent['sessionAttributes'] is not None else {}
    
    slots = intent["currentIntent"]["slots"]
    weight_slot = slots["weight"]
    logger.debug("violet")
    logger.debug(weight_slot)
    if not weight_slot:
        weight = get_weight(slots)
        if not weight:
            return delegate(session_attributes, slots)
    else:
        add_weight(weight_slot)
        weight = weight_slot

    return process_food(slots, int(weight))

def dispatch(intent_request):
    intent_name = intent_request['currentIntent']['name']
    # Dispatch to your bot's intent handlers
    if intent_name == WEIGHT_INTENT_NAME:
        return weight_control(intent_request)

    raise Exception('Intent with name ' + intent_name + ' not supported')

def handler(event, context):
    os.environ['TZ'] = 'America/New_York'
    time.tzset()
    global username
    username = event['userId']
    logger.debug('event.bot.name={}'.format(event['bot']['name']))
    return dispatch(event)
