import logging
import os, time
import json
import boto3, dynamo


logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

WEIGHT_INTENT_NAME='WeightIntent'
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

def add_weight(slots, weight):
    dynamo.put_item_weight(username, weight)
    logger.debug("Set {} weight = {}".format(username, weight))
    content = "Your weight is set!"
    return fulfill(content)  

def weight(intent):
    session_attributes = intent['sessionAttributes'] if intent['sessionAttributes'] is not None else {}
    slots = intent["currentIntent"]["slots"]
    weight_slot = slots["weight"]
    logger.debug("violet")
    logger.debug(weight_slot)
    if not weight_slot:
        return delegate(session_attributes, slots)
    else:
        return add_weight(slots, weight_slot)

def dispatch(intent_request):
    intent_name = intent_request['currentIntent']['name']
    # Dispatch to your bot's intent handlers
    if intent_name == WEIGHT_INTENT_NAME:
        return weight(intent_request)

    raise Exception('Intent with name ' + intent_name + ' not supported')

def handler(event, context):
    os.environ['TZ'] = 'America/New_York'
    time.tzset()
    global username
    username = event['userId']
    logger.debug('event.bot.name={}'.format(event['bot']['name']))
    return dispatch(event)
