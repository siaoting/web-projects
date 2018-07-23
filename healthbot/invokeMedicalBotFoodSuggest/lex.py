import logging
import os, time
import json
import boto3


logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

FOOD_SUGGEST_INTENT_NAME='FoodSuggestIntent'
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

def foodSuggest(intent):
    session_attributes = intent['sessionAttributes'] if intent['sessionAttributes'] is not None else {}
    slots = intent["currentIntent"]["slots"]
    calories_slot = slots["calories"]
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
    content = "For {} calories, you can try {}".format(calories_slot, foodItem)
    return fulfill(content)

def dispatch(intent_request):
    intent_name = intent_request['currentIntent']['name']
    # Dispatch to your bot's intent handlers
    if intent_name == FOOD_SUGGEST_INTENT_NAME:
        return foodSuggest(intent_request)

    raise Exception('Intent with name ' + intent_name + ' not supported')

def handler(event, context):
    os.environ['TZ'] = 'America/New_York'
    time.tzset()
    global username
    username = event['userId']
    logger.debug('event.bot.name={}'.format(event['bot']['name']))
    return dispatch(event)

